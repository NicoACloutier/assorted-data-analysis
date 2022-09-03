def main():
    import pandas as pd
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
    
    chengyu_df = pd.read_csv('all-sentences.csv')
    del chengyu_df['Unnamed: 0']
    sentences = chengyu_df['sentences'].to_list()
    
    model = AutoModelForSequenceClassification.from_pretrained('uer/roberta-base-finetuned-chinanews-chinese')
    tokenizer = AutoTokenizer.from_pretrained('uer/roberta-base-finetuned-chinanews-chinese')
    text_classification = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
    
    classified = []
    for sentence in sentences:
        try:
            classified.append(text_classification(sentence)[0]['label'])
        except Exception:
            classified.append('None')
    chengyu_df['classified'] = classified
    
    chengyu_df.to_csv('all-sentences.csv')

if __name__ == '__main__':
    main()