def main():
    import pandas as pd
    import re
    from pypinyin import pinyin

    chengyu = pd.read_csv('chengyu-appearances.csv') #get appearing chengyu
    del chengyu['Column1'] #delete unnecessary column
    appearing_idioms = chengyu['Chengyu'].to_list() #write series of chengyu to list
    
    #create meaning dictionary
    filename = 'ankideck-raw.txt' #file with chengyu and definitions on it
    file = open(filename, 'r', encoding='utf8') #open file
    raw_text = file.read() #extract text
    file.close() #close file
    chengyu_list = re.findall('(?<=<div id=""ent"">)....(?=</div> <div id=""from"">)', raw_text) #find all chengyu
    definition_list = re.findall('(?<=<span id=""from_content"">).+?(?=</span> </div>)', raw_text) #find all definitions
    explain_list = re.findall('(?<=<span id=""trans_content"">).+?(?=</span>)', raw_text) #find all explanations
    
    meaning_dict = dict() #create a meaning dictionary
    for i, idiom in enumerate(chengyu_list):
        definition = definition_list[i] #fetch definition
        meaning_dict[idiom] = definition #set meaning_dict for that chengyu to the definition
    
    explain_dict = dict() #create a meaning dictionary
    for i, idiom in enumerate(chengyu_list):
        explanation = explain_list[i] #fetch definition
        explain_dict[idiom] = explanation #set meaning_dict for that chengyu to the definition
    
    #add definition column to dataframe
    definition_list = []
    for idiom in appearing_idioms:
        meaning = meaning_dict[idiom] #fetch meaning
        definition_list.append(meaning) #add to list of appearing definitions
    chengyu['Definition'] = definition_list #add definitions column to dataframe
    
    #add explanation column to dataframe
    explain_list = []
    for idiom in appearing_idioms:
        explanation = explain_dict[idiom] #fetch explanation
        explain_list.append(explanation) #add to list of appearing explanations
    chengyu['Explanation'] = explain_list #add explanations column to dataframe
    
    #add frequency score out of 5 column to dataframe
    scores = []
    appearances = chengyu['Appearances'].to_list() #get list of appearances
    for appearance in appearances:
        if appearance > 50: scores.append(5) #append 5 if more than 50
        elif appearance > 20: scores.append(4) #append 4 if between 21 and 50
        elif appearance > 5: scores.append(3) #append 3 if between 6 and 20
        elif appearance > 1: scores.append(2) #append 2 if between 2 and 5
        elif appearance == 1: scores.append(1) #append 1 if it appears
        else: scores.append(0) #otherwise, append 0
    chengyu['Frequency'] = scores #add frequency column to dataframe
    
    #get pinyin
    pinyin_list = []
    for idiom in appearing_idioms:
        pinyin_list.append(' '.join([item[0] for item in pinyin(idiom)])) #convert chengyu to pinyin
    chengyu['Pinyin'] = pinyin_list
    
    #get english definitions
    definitions = []
    english = pd.read_csv('en-definitions.csv') #read translated csv
    en_chengyu = english['Chengyu'].to_list() #get chengyu
    en_defs = english['Definition'].to_list() #get definitions
    en_dict = dict(zip(en_chengyu, en_defs)) #make dictionary
    #put definitions in right order
    for idiom in appearing_idioms:
        definition = en_dict[idiom]
        definitions.append(definition)
    chengyu['English Definition'] = definitions #make english definition column
    
    #get english explanations
    explanations = []
    english = pd.read_csv('en-explanations.csv') #read translated csv
    en_chengyu = english['Chengyu'].to_list() #get chengyu
    en_explain = english['Explanation'].to_list() #get explanations
    en_dict = dict(zip(en_chengyu, en_explain)) #make dictionary
    #put explanations in right order
    for idiom in appearing_idioms:
        explanation = en_dict[idiom]
        explanations.append(explanation)
    chengyu['English Explanation'] = explanations #make english explanation column
    
    #get an example sentence for each chengyu
    examples = []
    text_df = pd.read_csv('train.csv', encoding='utf8') #read text csv
    texts = text_df['content'].to_list() #get sentence list
    texts = ' '.join(texts) #add to one text
    for idiom in appearing_idioms:
        example = re.search(f'(?<=[。！？.!? ]).+?{idiom}.+?[ 。！？.!?]', texts) #search for sentences including the idiom
        if example: example = example.group() #get example sentence
        else: example = 'None' #if none, append None
        examples.append(example) #append
    chengyu['Example'] = examples #add example sentence column to dataframe
    
    chengyu.to_csv('Chengyu-Final.csv') #write final dataframe to csv

if __name__ == '__main__':
    main()