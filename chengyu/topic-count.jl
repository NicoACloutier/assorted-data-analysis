using DataFrames
using CSV
using DataStructures

#function to find the most common value in a counter
mostcommon(c::Accumulator) = mostcommon(c, 1) #if no length is given, find 1st most common value
mostcommon(c::Accumulator, k) = sort(collect(c), by=kv->kv[2], rev=true)[1:k]


#the purpose of the following two functions is to account for a disparity
#in the presence of different topics in the sentence list. sentences labeled
#"mainland China politics" are vastly overrepresented, so the next functions attempt
#to account for this difference by multiplying the presence of other topics in the topics counter
#by a value equal to the amount of times the most common value appears over the amount of times
#it appears.

#function to find how much the number of appearances of each unique item in a list
#should be adjusted by to get it to the same value as the most commom key (rounded to integer)
function findadjustments(topiclist)
	finaldict = Dict()
	classifiedcounter = counter(topiclist) #create counter of list
	commonvalue = mostcommon(classifiedcounter) #find most common
	commonvalue, _ = first(commonvalue) #find key for most common value
	appearances = classifiedcounter[commonvalue] #find the number of appearances
	for (value, tempappearances) in classifiedcounter
		adjustment = appearances / tempappearances #find adjustment (most common appearances divided by that value's appearances)
		finaldict[value] = round(Int, adjustment) #round to integer
	end
	finaldict["None"] = 1 #set "None" to 1 (to avoid it being selected)
	finaldict
end

#adjust the values of an input counter by values prescribed in a dictionary
function adjust(inputcounter, adjustmentdict)
	for (topic, adjustment) in adjustmentdict
		inputcounter[topic] *= adjustment #adjust value
	end
	inputcounter
end

#get the classifications for each chengyu appearing in a list of sentences.
#(third argument is dictionary of sentences to their classifications, fourth
#is the dictionary of adjustments to counter values)
function getclassifications(wordlist, sentencelist, classifications, adjustdict)
	topics = []
	for word in wordlist
		sentences = [sentence for sentence in sentencelist if occursin(word, sentence)] #get list of sentences word occurs in
		topiclist = [classifications[sentence] for sentence in sentences] #get topics of each sentence
		topiccounter = counter(topiclist) #create counter of topics
		topiccounter = adjust(topiccounter, adjustdict) #adjust counter for presence disparity of different topics
		if isempty(topiccounter)
			topic = "None" #set topic to none if no sentences were found
		else
			topic = mostcommon(topiccounter) #find the key with the highest value in the counter
			topic, _ = first(topic) #get the key
		end
		push!(topics, topic) #add the key to the list of topics
	end
	topics
end

chengyudf = DataFrame(CSV.File("chengyu-appearances.csv")) #open chengyu csv
sentencedf = DataFrame(CSV.File("all-sentences.csv")) #open sentence csv
chengyulist = collect(chengyudf.Chengyu) #get list of chengyu
sentencelist = collect(sentencedf.sentences) #get list of sentences
classifiedlist = collect(sentencedf.classified) #get list of topics (aligned to sentence list)

adjustdict = findadjustments(classifiedlist) #find the adjustments for the topic list

sentences = Dict(zip(sentencelist, classifiedlist)) #create a dictionary of sentences to their topics

classifications = getclassifications(chengyulist, sentencelist, sentences, adjustdict) #get the classifications of each chengyu

chengyudf.Topic = classifications #add to chengyu dataframe

CSV.write("chengyu-appearances.csv", chengyudf) #write to csv