def main():
    
    import pandas as pd
    
    #improperly rendered punctuation
    replacements = {
    "&quot;": '"',
    "·": ", ",
    "&#39;": "'"
    }
    
    #replace above dictionary with proper punctuation
    def beautify(sentence, replacement_dict):
        for key in replacement_dict:
            sentence = sentence.replace(key, replacement_dict[key])
        return sentence
    
    final_chengyu = []
    final_sentences = []
    
    for x in [x+1 for x in range(20)]:
        temp_df = pd.read_csv(f"en-definitions\\en-definitions{x}.csv") #open up csvs 1-20
        temp_chengyu = temp_df["Chengyu"].to_list() #get chengyu
        temp_sentences = temp_df["Definitions"].to_list() #get definitions
        temp_sentences = [beautify(sentence, replacements) for sentence in temp_sentences] #beautify sentences
        final_chengyu += temp_chengyu #add to list
        final_sentences += temp_sentences #add to list
    
    output_df = pd.DataFrame([final_chengyu, final_sentences], ["Chengyu", "Definition"]) #make output dataframe
    output_df = output_df.transpose() #transpose
    output_df.to_csv("en-definitions.csv") #write to csv

if __name__ == '__main__':
    main()