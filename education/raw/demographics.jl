using CSV
using DataFrames

allschoolsdf = DataFrame(CSV.File("schools.csv")) #get df of schools
dropmissing!(allschoolsdf) #get rid of rows with missing
schoolids = unique(allschoolsdf.CDSCode) #get unique school ids

genders = ["M", "F"] #genders in dataset
races = range(1, 7) #races in dataset (numbered 1-7)

basic = "raw\\demographics\\filesenr" #basic file template
numfiles = 6 #number of files
lowest = 16 #lowest year (2016)

df = DataFrame(CDSCode=[], Year=[], 
			   M1=[], M2=[], M3=[], M4=[], M5=[], M6=[], M7=[], 
			   F1=[], F2=[], F3=[], F4=[], F5=[], F6=[], F7=[]) #dataframe with columns corresponding to gender/race pairs

for i in range(0, numfiles-1)
	file = "$(basic)$(lowest+i).csv" #filename
	tempdf = DataFrame(CSV.File(file)) #open file
	for id in schoolids
		school = Dict("CDSCode" => id, "Year" => lowest+i) #make dict with CDS code and year
		moretempdf = filter(row -> row.CDS_CODE == id, tempdf) #filter to only include data from one school
		allsum = sum(collect(moretempdf[:, "ENR_TOTAL"])) #get total sum
		for race in races
			evenmoretempdf = filter(row -> row.ETHNIC == race, moretempdf) #filter to only get data from one race
			for gender in genders
				value = sum(collect(filter(row -> row.GENDER == gender, evenmoretempdf)[:, "ENR_TOTAL"])) #filter to only get data from one gender
				percent = value / allsum #get percent of race/gender pair
				school["$(gender)$(race)"] = percent #add data point to school's dictionary
			end
		end
		push!(df, school) #add school's dictionary as row to final dataframe
	end
end

CSV.write("raw\\demographics.csv", df) #write to csv
