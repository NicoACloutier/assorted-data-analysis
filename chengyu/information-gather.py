def main():
    import pandas as pd
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
    import re
    
    model = AutoModelForSeq2SeqLM.from_pretrained('Helsinki-NLP/opus-mt-zh-en')
    tokenizer = AutoTokenizer.from_pretrained('Helsinki-NLP/opus-mt-zh-en')
    translate = pipeline('translation', model=model, tokenizer=tokenizer)

    chengyu = pd.read_csv('chengyu-appearances.csv')
    appearing_idioms = chengyu['Chengyu'].to_list()
    del chengyu['Unnamed: 0']
    
    filename = 'ankideck-raw.txt'
    file = open(filename, 'r', encoding='utf8')
    raw_text = file.read()
    chengyu_list = re.findall('(?<=<div id=""ent"">)....(?=</div> <div id=""from"">)', raw_text)
    definition_list = re.findall('(?<=<span id=""from_content"">).+?(?=</span> </div>)', raw_text)
    print(len(chengyu_list))
    print(len(definition_list))
    meaning_dict = dict()
    for i, chengyu in enumerate(chengyu_list):
        definition = definition_list[i]
        meaning_dict[chengyu] = definition
    
    definition_list = []
    for idiom in appearing_idioms:
        meaning = meaning_dict[idiom]
        definition_list.append(meaning)
    
    english_list = translate(definition_list)
    
    print(english_list[0])


if __name__ == '__main__':
    main()