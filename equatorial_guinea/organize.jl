using CSV
using DataFrames

function reorganize(df, newcolumns)
	outputdf = DataFrame()
	column = unique(collect(df[!, newcolumns]))
	for name in column
		temp_df = filter(row -> row.Name == name, df)
		outputdf[!, name] = temp_df
	end
end

df = DataFrame(CSV.File("data.csv"))
df = reorganize(df, "Name")