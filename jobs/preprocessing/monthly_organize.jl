using CSV
using DataFrames
using Languages

const DATA_DIR = "..\\data\\raw"
const OUTPUT_DIR = "..\\data\\cleaned"
const PROPORTION = 0.03 #proportion of job titles the word must appear in
const HOURS_PER_YEAR = 1800 #number of hours worked in a year for an hourly-payed job (1800 is roughly the US average)
const PUNCTUATION = [",", ".", "-", "!", "?", ":", ";", "'", "/", "&amp;"]

one_hot(wordlist, all_words) = [Int(in(word, wordlist)) for word in all_words]
appearances(word, wordlists) = sum([in(word, wordlist) for wordlist in wordlists])
remove_stopwords(wordlist) = [word for word in wordlist if !in(word, stopwords(Languages.English()))]
remove_punctuation(wordlist) = [word for word in wordlist if !in(word, PUNCTUATION)]

#turn a list of column names and row data into a dictionary
function to_dict(columns, rows)
	final_dict = Dict()
	for (i, column) in enumerate(columns)
		final_dict[column] = [row[i] for row in rows]
	end
	final_dict
end

#get all unique words out of a list of wordlists
function get_all_words(wordlists)
	all_words = []
	for wordlist in wordlists
		all_words = cat(all_words, wordlist; dims=1)
	end
	all_words |> unique |> remove_stopwords |> remove_punctuation
end

#remove words in a series of wordlists that only appear below
#a certain proportion of worlists, return all words other than these
function whittle(wordlists, proportion)
	all_words = get_all_words(wordlists)
	number_wordlists = length(wordlists)
	proportions = [appearances(word, wordlists)/number_wordlists for word in all_words]
	[all_words[i] for (i, proportion) in enumerate(proportions) if proportion > PROPORTION]
end

#get the one hot encodings
function find_words(titles)
	titles = [title |> lowercase |> split |> unique for title in titles]
	all_words = whittle(titles, PROPORTION)
	titles = [one_hot(title, all_words) for title in titles]
	(all_words, titles)
end

#parse a wage string
function parse_wage(wage)
	try
		captured_wage = match(r"\$([0-9]+?\.[0-9]+?) - \$([0-9]+?\.[0-9]+?) Per Hour", wage).captures
		low = parse(Float64, captured_wage[1])
		high = parse(Float64, captured_wage[2])
		return (high + low) / 2 * HOURS_PER_YEAR
	catch
		captured_wage = match(r"\$([0-9]+?\.[0-9]+?) Per Hour", wage).captures
		wage = parse(Float64, captured_wage[1])
		return (wage) / 2 * HOURS_PER_YEAR
	end
end

#parse a salary string
function parse_salary(salary)
	try
		captured_salary = match(r"\$([0-9]+?)K - \$([0-9]+?)K", salary).captures
		low = parse(Float64, captured_salary[1])
		high = parse(Float64, captured_salary[2])
		return (high + low) / 2 * 1000
	catch
		captured_salary = match(r"\$([0-9]+?)K", salary).captures
		salary = parse(Float64, captured_salary[1])
		return (salary) / 2 * 1000
	end
end

#parse a pay string
function parse_pay(pay)
	if ismissing(pay)
		return missing
	elseif occursin("Per Hour", pay)
		return parse_wage(pay)
	else
		return parse_salary(pay)
	end
end

function main()
	df = DataFrame(CSV.File("$(DATA_DIR)\\raw.csv"))
	
	df[!, "Parsed_Salary"] = map(parse_pay, df[!, "Salary"])
	
	(all_words, titles) = find_words(df[!, "Title"])
	title_df = DataFrame(to_dict(all_words, titles))
	title_df[!, "Salary"] = df[!, "Parsed_Salary"]
	title_df[!, "Date"] = df[!, "Date"]
	
	CSV.write("$(OUTPUT_DIR)\\titles.csv", title_df)
	
	geography_df = DataFrame()
	geography_df[!, "Location"] = df[!, "Location"]
	geography_df[!, "Salary"] = df[!, "Parsed_Salary"]
	geography_df[!, "Date"] = df[!, "Date"]
	
	CSV.write("$(OUTPUT_DIR)\\geography.csv", geography_df)
	
	company_df = DataFrame()
	company_df[!, "Company"] = df[!, "Company"]
	company_df[!, "Salary"] = df[!, "Parsed_Salary"]
	company_df[!, "Date"] = df[!, "Date"]
	
	CSV.write("$(OUTPUT_DIR)\\companies.csv", company_df)
	
end

main()