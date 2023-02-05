using SQLite
using CSV
using DataFrames

const DATA_DIR = "..\\data\\cleaned"

#convert list of column names to string for SQLite query
function to_string(column_list)
	str = ""
	for column in column_list
		if (isnothing(match(r"[./,-]", column)))
			str *= "$(column) INTEGER, "
		end
	end
	str
end

function remove_single_quote(str)
	replace(str, "'" => "")
end

function to_values(df)
	special_columns = ["PostingID", "Salary", "Date"]
	str = ""
	columns = [name for name in names(df) if !in(name, special_columns)]
	
	for row in eachrow(df)
		posting_id = row.PostingID
		salary = row.Salary
		date = row.Date
		
		str *= "($(posting_id), "
		for column in columns
			value = row[column]
			value = remove_single_quote(value)
			str *= "'$(value)', "
		end
		str *= "$(salary), '$(date)'), "
	end
	len = length(str)
	str = str[1:len-2]
	str = replace(str, "missing" => "NULL")
	return str
end

function main()
	title_df = DataFrame(CSV.File("$(DATA_DIR)\\titles.csv"))
	columns = [item for item in names(title_df) if item != "Salary" && item != "Date"]
	column_string = to_string(columns)
	company_df = DataFrame(CSV.File("$(DATA_DIR)\\companies.csv"))
	location_df = DataFrame(CSV.File("$(DATA_DIR)\\geography.csv"))
	
	company_df[!, "PostingID"] = range(1, nrow(company_df))
	location_df[!, "PostingID"] = range(1, nrow(location_df))

	db = SQLite.DB("$(DATA_DIR)\\jobs.db")
	SQLite.execute(db, "CREATE TABLE IF NOT EXISTS Companies(PostingID INTEGER, Company TEXT, Salary INTEGER, Date TEXT)")
	SQLite.execute(db, "CREATE TABLE IF NOT EXISTS Geography(PostingID INTEGER, Location TEXT, Salary INTEGER, Date BLOB);")
	
	df_values = to_values(company_df)
	query = "INSERT INTO Companies(PostingID, Company, Salary, Date) VALUES $(df_values);"
	SQLite.execute(db, query)
	
	df_values = to_values(location_df)
	query = "INSERT INTO Geography(PostingID, Location, Salary, Date) VALUES $(df_values);"
	SQLite.execute(db, query)
end

main()