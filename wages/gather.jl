using DataFrames
using CSV

const VALUE_COLUMNS = ["Workforce", "Worked Hours Week", "Worked Days Week", "Monthly Wage", "Workforce MOE"]

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

function make_df(format_df, unwanted_columns, wanted_column, value_columns)
	other_columns = ["Sex", wanted_column]
	df = empty(format_df)
	wanted_column_value_list = unique(format_df[:, wanted_column])
	
	for unwanted_column in unwanted_columns
		if !(in(unwanted_column, other_columns))
			df = select(df, Not(unwanted_column))
		end
	end
	
	for wanted in wanted_column_value_list
		tempdf = filter(row -> row[wanted_column] == wanted, format_df)
		for gender in ["Mujer", "Hombre"]
			row = Vector{Any}()
			push!(row, wanted)
			push!(row, gender)
			for value_column in value_columns
				temp_avg = avg_from_row_value(tempdf, "Sex", gender, value_column)
				if temp_avg == Float64(NaN) || temp_avg == Missing
					push!(row, Missing)
				else
					push!(row, trunc(temp_avg))
				end
			end
			push!(df, row)
		end
	end
	df
	end

df = DataFrame(CSV.File("raw\\raw.csv"))
df = clean_df(df)
unwanted = [column for column in names(df) if !in(column, VALUE_COLUMNS)]

wanted_columns = ["Municipality", "Sector", "Year"]
for column in wanted_columns
	temp_df = make_df(df, unwanted, column, VALUE_COLUMNS)
	CSV.write("$(column).csv", temp_df)
end
