using Statistics
using CSV
using DataFrames

#get basic statistical information for a vector of data
function basicinfo(name, column)
	#column = removemissing(column)
	Dict("name"=>name,
	"mean"=>mean(column),
	"stdev"=>stdm(column, mean(column)),
	"var"=>var(column))
end

#find all correlations between columns in a dataframe
function correlations(allnames, df, rxpattern)
	correlationlist = []
	allnames = [name for name in allnames if !isnothing(match(rxpattern, name))]
	for firstname in allnames
		for secondname in allnames
			if firstname !== secondname
				firstcolumn = df[:, firstname]
				secondcolumn = df[:, secondname]
				tempcorrelation = cor(firstcolumn, secondcolumn)
				toadd = Dict("names"=>"$(firstname), $(secondname)", 
				"correlation"=>tempcorrelation)
				push!(correlationlist, toadd)
			end
		end
	end
	correlationlist
end

#sort correlations in list of dictionaries
function sortcors(corlist)
	tosort = [(-item["correlation"], item["names"]) for item in corlist]
	[[-item[1], item[2]] for item in sort(tosort)]
end

#turn correlations to dataframe
function correlationtodf(correlations)
	correlationlist = [item[1] for item in sorted]
	bothlist = [split(item[2], ", ") for item in sorted]
	firstlist = [clean(item[1]) for item in bothlist]
	secondlist = [clean(item[2]) for item in bothlist]	
	unique(DataFrame("CORRELATIONS"=>correlationlist,
	"FIRST"=>firstlist, "SECOND"=>secondlist), 1)
end

#put the disease names in a more presentable form
clean(diseasename) = lowercase(replace(diseasename, "_CrudePrev"=>""))

#get basic statistical information about all columns in a dataframe whose name matches a regex pattern
getbasic(allnames, df, rxpattern) = [basicinfo(name, df[:, name]) for name in allnames if !isnothing(match(rxpattern, name))]

df = DataFrame(CSV.File("data.csv")) #get data
dropmissing!(df) #get rid of missing rows
select!(df, r"StateAbbr|PlaceName|.+_CrudePrev") #select appropriate columns
columns = names(df) #get column names
rx = r".+_CrudePrev" #define regex pattern for columns with numerical info

correlationlist = correlations(columns, df, rx) #get correlations
sorted = sortcors(correlationlist) #sort correlation list
outputdf = correlationtodf(sorted) #make output dataframe
CSV.write("correlations.csv", outputdf) #write to csv

columninfo = getbasic(columns, df, rx) #get basic information for columns with numerical info in df