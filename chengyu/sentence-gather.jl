using DataFrames
using CSV

function collectsentences(wordlist, text)
	wordstring = join(wordlist, "|")
	rx = Regex(string("(?<=[。！？.!? ]).+?(", wordstring, ").+?[ 。！？.!?]"))
	captured = eachmatch(rx, text)
	[item.match for item in captured]
end
	
chengyudf = DataFrame(CSV.File("data\\chengyu-appearances.csv"))
chengyulist = collect(chengyudf.Chengyu)

textdf = DataFrame(CSV.File("train.csv"))
textlist = collect(textdf.content)
text = join(textlist, " ")

sentencelist = collectsentences(chengyulist, text)

output_df = DataFrame(sentences=sentencelist)

CSV.write("data\\all-sentences.csv", output_df)