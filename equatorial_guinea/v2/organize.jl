using CSV
using DataFrames

#reorganize the dataframe to have the cities be column names
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

#subtract aligned items from named columns in a dataframe when
#given an aligned list of items to subtract by
function subtractcontrol(columnlist, df, controlvalues)
	controlled = []
	for column in columnlist
		columnvalues = collect(df[:, column])
		columnvalues = [value-controlvalues[i] for (i, value) in enumerate(columnvalues)]
		push!(controlled, (column, columnvalues))
	end
	controlled
end

#make a dataframe with a list of tuples with the first value being column names
#and the second value being the column itself
function makedf(namevaluetuple)
	df = DataFrame()
	for namevalue in namevaluetuple
		name = namevalue[1]
		value = namevalue[2]
		df[!, name] = value
	end
	df
end

df = DataFrame(CSV.File("data.csv"))
df = reorganize(df, "Name")
columns = names(df)
controlvalues = collect(df[:, "Control"])
deleteat!(columns, 1)

namevaluetuple = subtractcontrol(columns, df, controlvalues)
df = makedf(namevaluetuple)

CSV.write("data.csv", df)
