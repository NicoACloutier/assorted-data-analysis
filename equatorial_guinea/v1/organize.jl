using CSV
using DataFrames

function reorganize(df, newcolumns)
	outputdf = DataFrame()
	column = unique(collect(df[:, newcolumns]))
	outputdf.Date = unique(collect(df[:, "Date"]))
	all_values = []
	all_names = []
	for name in column
		temp_df = filter(row -> row.Name == name, df)
		temp = collect(temp_df[:, "Value"])
		outputdf[!, name] = temp
	end
	outputdf
end

df = DataFrame(CSV.File("data.csv"))
df = reorganize(df, "Name")
CSV.write("data.csv", df)