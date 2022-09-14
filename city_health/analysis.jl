using Statistics
using CSV
using DataFrames

#get basic statistical information for a vector of data
function basicinfo(name, column)
	column = removemissing(column)
	Dict("name"=>name,
	"mean"=>mean(column),
	"stdev"=>stdm(column, mean(column)),
	"var"=>var(column))
end

#find all correlations between columns in a dataframe
function correlations(allnames, df, rxpattern)
	allnames = [name for name in allnames if !isnothing(match(rxpattern, name))]
	for firstname in allnames
		for secondname in allnames
			firstcolumn = df[:, firstname]
			secondcolumn = df[:, secondname]
		end
	end
end

#remove rows with missing values in two-dimensional arrays
function doubleremovemissing(twodimensional)
	
end

#remove missing values of a collection
removemissing(collection) = [item for item in collection if (item !== missing)]

#get basic statistical information about all columns in a dataframe whose name matches a regex pattern
getbasic(allnames, df, rxpattern) = [basicinfo(name, df[:, name]) for name in allnames if !isnothing(match(rxpattern, name))]

df = DataFrame(CSV.File("data.csv")) #get data
select!(df, r"StateAbbr|PlaceName|.+_CrudePrev") #select appropriate columns
columns = names(df) #get column names
rx = r".+_CrudePrev" #define regex pattern for columns with numerical info
columninfo = getbasic(columns, df, rx) #get basic information for columns with numerical info in df
