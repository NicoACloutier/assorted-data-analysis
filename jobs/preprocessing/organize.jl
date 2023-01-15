using CSV
using DataFrames
using Languages

const DATA_DIR = "..\\data\\raw"
const OUTPUT_DIR = "..\\data\\cleaned"
const PROPORTION = 0.05
const PUNCTUATION = [",", ".", "-", "!", "?", ":", ";", "'"]

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

function main()
	df = DataFrame(CSV.File("$(DATA_DIR)\\raw.csv"))
	
	(all_words, titles) = find_words(df[!, "Title"])
	println(titles)
	title_df = DataFrame(to_dict(all_words, titles))
	CSV.write("$(OUTPUT_DIR)\\titles.csv", title_df)
	
end

main()