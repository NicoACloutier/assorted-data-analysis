using DataFrames
using CSV
using DataStructures

mostcommon(c::Accumulator) = mostcommon(c, length(c))
mostcommon(c::Accumulator, k) = sort(collect(c), by=kv->kv[2], rev=true)[1:k]

function getclassifications(wordlist, sentencelist, classifications)
	topics = []
	for word in wordlist
		sentencelist = [sentence for sentence in sentencelist if word in sentence]
		topiclist = [classifications[sentence] for sentence in sentencelist]
		topiccounter = counter(topiclist)
		topic = mostcommon(topiccounter)
		push!(topics, topic)
	end
end

chengyudf = DataFrame(CSV.File("all-chengyu.csv"))
sentencedf = DataFrame(CSV.File("all-sentences.csv"))
chengyulist = collect(chengyudf.Chengyu)
sentencelist = collect(sentencedf.sentences)
classifiedlist = collect(sentencedf.classified)

sentences = Dict(sentencelist[i]=>classifiedlist[i] for i = 1:length(sentencelist))

classifications = getclassifications(chengyulist, sentencelist, classifiedlist)

chengyudf.topics = classifications

print(chengyudf)