using CSV
using DataFrames

allschoolsdf = DataFrame(CSV.File("schools.csv"))
dropmissing!(allschoolsdf)
schoolids = unique(allschoolsdf.CDSCode)

genders = ["M", "F"]
races = range(1, 7)

basic = "raw\\demographics\\filesenr"
numfiles = 6
lowest = 16

df = DataFrame(CDSCode=[], Year=[], 
			   M1=[], M2=[], M3=[], M4=[], M5=[], M6=[], M7=[], 
			   F1=[], F2=[], F3=[], F4=[], F5=[], F6=[], F7=[])

for i in range(0, numfiles-1)
	file = "$(basic)$(lowest+i).csv"
	tempdf = DataFrame(CSV.File(file))
	for id in schoolids
		school = Dict("CDSCode" => id, "Year" => lowest+i)
		moretempdf = filter(row -> row.CDS_CODE == id, tempdf)
		allsum = sum(collect(moretempdf[:, "ENR_TOTAL"]))
		for race in races
			evenmoretempdf = filter(row -> row.ETHNIC == race, moretempdf)
			for gender in genders
				value = sum(collect(filter(row -> row.GENDER == gender, evenmoretempdf)[:, "ENR_TOTAL"]))
				percent = value / allsum
				school["$(gender)$(race)"] = percent
			end
		end
		push!(df, school)
	end
end

CSV.write("raw\\demographics.csv", df)
