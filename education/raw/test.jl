using CSV
using DataFrames

allschoolsdf = DataFrame(CSV.File("schools.csv")) #get df of schools
dropmissing!(allschoolsdf) #get rid of rows with missing

basic = "raw\\test\\test" #basic file template
years = [16, 17, 18, 19, 21]

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

for year in years
	yeardf = DataFrame(CSV.File("$(basic)20$(year).csv")) #open df for that year
	yeardf = select(yeardf, r"Code|Percentage Standard") #get only rows with Code or Percentage Standard in the title
	yeardf[!, "School Code"] = [getid(col) for col in eachrow(yeardf)] #set School Code column to combined school codes
	yeardf = select(yeardf, r"School Code|Percent") #select only rows with Percent or School Code in the title (get rid of old code columns)
	yeardf = filter(row -> row["School Code"] != 0, yeardf) #get rid of the school code 0 (for the overall California school system)
	CSV.write("$(basic)$(year)-cut.csv", yeardf) #write to csv
end
