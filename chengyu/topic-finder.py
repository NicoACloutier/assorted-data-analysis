def main():
    import pandas as pd
    import re
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
    from collections import Counter
    
    chengyu_df = pd.read_csv('all-sentences.csv')
    sentences = chengyu_df['sentences'].to_list()
    
    model = AutoModelForSequenceClassification.from_pretrained('uer/roberta-base-finetuned-chinanews-chinese')
    tokenizer = AutoTokenizer.from_pretrained('uer/roberta-base-finetuned-chinanews-chinese')
    text_classification = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)

    classified = [item['label'] for item in text_classification(sentences)]
    chengyu_df['classified'] = classified
    
    chengyu_df.to_csv('all-sentences.csv')

if __name__ == '__main__':
    main()