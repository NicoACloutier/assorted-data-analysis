using SQLite
using CSV
using DataFrames

const DATA_DIR = "..\\data\\cleaned"

function no_punctuation(str)
	isnothing(match(r"[./,-]", str))
end

#convert list of column names to string for SQLite query
function to_string(column_list)
	str = ""
	column_list = [column for column in column_list if no_punctuation(column)]
	for column in column_list
		str *= "$(column) INTEGER, "
	end
	str
end

function get_name_strings(df, add_type)
	special_columns = ["PostingID", "Salary", "Date"]
	str = ""
	columns = [name for name in names(df) if !in(name, special_columns)]
	columns = [name for name in columns if no_punctuation(name)]
	for column in columns
		if add_type
			str *= "$(column) INTEGER, "
		else
			str *= "$(column), "
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
	columns = [name for name in columns if no_punctuation(name)]
	
	for row in eachrow(df)
		posting_id = row.PostingID
		salary = row.Salary
		date = row.Date
		
		str *= "($(posting_id), "
		for column in columns
			value = row[column]
			value = remove_single_quote(string(value))
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
	title_df[!, "PostingID"] = range(1, nrow(title_df))

	db = SQLite.DB("$(DATA_DIR)\\jobs.db")
	SQLite.execute(db, "CREATE TABLE IF NOT EXISTS Companies(PostingID INTEGER, Company TEXT, Salary INTEGER, Date TEXT)")
	SQLite.execute(db, "CREATE TABLE IF NOT EXISTS Geography(PostingID INTEGER, Location TEXT, Salary INTEGER, Date BLOB)")
	title_columns = get_name_strings(title_df, true)
	SQLite.execute(db, "CREATE TABLE IF NOT EXISTS Title(PostingID INTEGER, $(title_columns)Salary INTEGER, Date BLOB)")
	
	df_values = to_values(company_df)
	query = "INSERT INTO Companies(PostingID, Company, Salary, Date) VALUES $(df_values)"
	SQLite.execute(db, query)
	
	df_values = to_values(location_df)
	query = "INSERT INTO Geography(PostingID, Location, Salary, Date) VALUES $(df_values)"
	SQLite.execute(db, query)
	
	#remove columns not in db
	name_words = DataFrame(SQLite.DBInterface.execute(db, "PRAGMA TABLE_INFO(Title)"))[!, "name"]
	name_words = [name for name in name_words if name in names(title_df)]
	title_df = select(title_df, name_words)
	
	df_values = to_values(title_df)
	title_columns = get_name_strings(title_df, false)
	query = "INSERT INTO Title(PostingID, $(title_columns)Salary, Date) VALUES $(df_values)"
	SQLite.execute(db, query)
end

main()