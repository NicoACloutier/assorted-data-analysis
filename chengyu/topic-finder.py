def main():
    import pandas as pd
    import re
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
    from collections import Counter
    
    chengyu_dg = pd.read_csv('all-sentences.csv')
    del chengyu['Unnamed: 0']
    appearing_chengyu = chengyu_df['chengyu'].to_list()
    sentences = chengyu_df['sentences'].to_list()
    
    model = AutoModelForSequenceClassification.from_pretrained('uer/roberta-base-finetuned-chinanews-chinese')
    tokenizer = AutoTokenizer.from_pretrained('uer/roberta-base-finetuned-chinanews-chinese')
    text_classification = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)

    all_sentences = []
    for sentence in sentences:
        if isinstance(sentence, list):
            sentence = sentence.split(' ')
            all_sentences += sentence
    all_sentences = list(set(all_sentences))

    classified = text_classification(all_sentences)
    classified = [Counter(item['label']) for item in classified]
    
    topic_dict = dict()
    for i, sentence in enumarete(all_sentences):
        topic_counter = classified[i]
        topic = max(topic_counter, key=topic_counter.get)
        topic_dict[sentence] = topic
    
    topics_df.to_csv('topics.csv')

if __name__ == '__main__':
    main()