using DataFrames
using CSV
using DataStructures

mostcommon(c::Accumulator) = mostcommon(c, 1)
mostcommon(c::Accumulator, k) = sort(collect(c), by=kv->kv[2], rev=true)[1:k]

function findadjustments(topiclist)
	finaldict = Dict()
	classifiedcounter = counter(topiclist)
	commonvalue = mostcommon(classifiedcounter)
	commonvalue, _ = first(commonvalue)
	appearances = classifiedcounter[commonvalue]
	for (value, tempappearances) in classifiedcounter
		adjustment = appearances / tempappearances
		finaldict[value] = round(Int, adjustment)
	end
	finaldict["None"] = 1
	finaldict
end

function adjust(inputcounter, adjustmentdict)
	for (topic, adjustment) in adjustmentdict
		inputcounter[topic] *= adjustment
	end
	inputcounter
end

function getclassifications(wordlist, sentencelist, classifications, adjustdict)
	topics = []
	for word in wordlist
		sentences = [sentence for sentence in sentencelist if occursin(word, sentence)]
		topiclist = [classifications[sentence] for sentence in sentences]
		topiccounter = counter(topiclist)
		topiccounter = adjust(topiccounter, adjustdict)
		if isempty(topiccounter)
			topic = "None"
		else
			topic = mostcommon(topiccounter)
			topic, _ = first(topic)
		end
		push!(topics, topic)
	end
	topics
end

chengyudf = DataFrame(CSV.File("chengyu-appearances.csv"))
sentencedf = DataFrame(CSV.File("all-sentences.csv"))
chengyulist = collect(chengyudf.Chengyu)
sentencelist = collect(sentencedf.sentences)
classifiedlist = collect(sentencedf.classified)

adjustdict = findadjustments(classifiedlist)

sentences = Dict(zip(sentencelist, classifiedlist))

classifications = getclassifications(chengyulist, sentencelist, sentences, adjustdict)

chengyudf.Topic = classifications

CSV.write("chengyu-appearances.csv", chengyudf)