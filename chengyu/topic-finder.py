def main():
    import pandas as pd
    import re
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
    from collections import Counter
    
    chengyu = pd.read_csv('chengyu-appearances.csv')
    del chengyu['Unnamed: 0']
    appearing_idioms = chengyu['Chengyu'].to_list()
    
    model = AutoModelForSequenceClassification.from_pretrained('uer/roberta-base-finetuned-chinanews-chinese')
    tokenizer = AutoTokenizer.from_pretrained('uer/roberta-base-finetuned-chinanews-chinese')
    text_classification = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)

    topics = []
    text_df = pd.read_csv('train.csv', encoding='utf8')
    texts = text_df['content'].to_list()
    texts = ' '.join(texts)
    for i, idiom in enumerate(appearing_idioms):
        examples = re.findall(f'(?<=[。！？.!? ]).+?{idiom}.+?[ 。！？.!?]', texts)
        try:
            if examples:
                topics = text_classification(examples)
                topics = [item['label'] for item in topics]
                topics = Counter(topics)
                counts = [topics[item] for item in topics]
                topics = list(topics)
                maximum = max(counts)
                max_index = counts.index(maximum)
                topic = topics[max_index]
                topics.append(topic)
            else: topics.append('None')
        except Exception:
            topics.append('None')
    
    topics_df = pd.DataFrame([appearing_idioms, topics], ['Chengyu', 'Topic'])
    
    topics_df.to_csv('topics.csv')

if __name__ == '__main__':
    main()