using CSV
using DataFrames

allschoolsdf = DataFrame(CSV.File("schools.csv")) #get df of schools
dropmissing!(allschoolsdf) #get rid of rows with missing
schoolids = unique(allschoolsdf.CDSCode) #get unique school ids

basic = "raw\\frpm\\frpm" #basic file template
numfiles = 6 #number of files
lowest = 16 #lowest year (2016)

function addzeros(str, len)
	difference = len - length(str)
	repeat("0", difference) * str
end

#function to return full school code given a row of school data
#(for this data file they split the school code into individual
#county, district, and school codes despite doing it differently
#on other files)
function getid(schoolrow)
	county = addzeros(string(schoolrow[1]), 2)
	district = addzeros(string(schoolrow[2]), 5)
	school = addzeros(string(schoolrow[3]), 7)
	parse(Int, "$(county)$(district)$(school)")
end

for i in range(0, numfiles-1)
	year = lowest+i
	yeardf = DataFrame(CSV.File("$(basic)$(year).csv"))
	yeardf = select(yeardf, r"Code|Percent[\S\s]+?FRPM[\S\s]+?17")
	yeardf[!, "School Code"] = [getid(col) for col in eachrow(yeardf)]
	yeardf = select(yeardf, r"School Code|Percent")
	CSV.write("$(basic)$(year)-cut.csv", yeardf)
end
