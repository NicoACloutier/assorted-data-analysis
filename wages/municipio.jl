using DataFrames
using CSV

function avg_from_row_value(df, column_with_value, value, column_to_avg)
	df = filter(row -> row[column_with_value] == value, df)
	valuelist = collect(df[:, column_to_avg])
	try
		return sum(valuelist)/length(valuelist)
	catch
		return Missing
	end
end

function clean_df(df)
	for column in names(df)
		df[!, column] = replace(df[:, column], NaN => Missing)
	end
	dropmissing(df)
end

df = DataFrame(CSV.File("raw\\raw.csv"))
df = clean_df(df)
municipalities = unique(df[:, "Municipality"])
wanted = ["Workforce", "Worked Hours Week", "Worked Days Week", "Monthly Wage", "Workforce MOE"]
unwanted = [column for column in names(df) if !in(column, wanted)]
other_columns = ["Sex", "Municipality"]

municipality_df = empty(df)
for unwanted_column in unwanted
	if !(in(unwanted_column, other_columns))
		global municipality_df = select(municipality_df, Not(unwanted_column))
	end
end

for municipality in municipalities
	tempdf = filter(row -> row.Municipality == municipality, df)
	for gender in ["Mujer", "Hombre"]
		row = Vector{Any}()
		push!(row, municipality)
		push!(row, gender)
		for wanted in wanted
			temp_avg = avg_from_row_value(tempdf, "Sex", gender, wanted)
			if temp_avg == Float64(NaN) || temp_avg == Missing
				push!(row, Missing)
			else
				push!(row, trunc(temp_avg))
			end
		end
		push!(municipality_df, row)
	end
end

CSV.write("municipality.csv", municipality_df)
