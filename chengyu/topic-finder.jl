using DataFrames
using CSV

function collectsentences(wordlist)
	for i, word in enumerate(wordlist)
	
	end
end
	
chengyudf = DataFrame(CSV.File("chengyu-appearances.csv"))
chengyulist = collect(chengyudf.Chengyu)
