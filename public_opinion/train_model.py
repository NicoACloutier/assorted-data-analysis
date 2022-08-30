def main():
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
    import numpy as np
    import pandas as pd
    import torch
    import random
    import re
    
    #initialize pretrained model
    pretrained_name = 'facebook/bart-large-mnli'
    tokenizer = AutoTokenizer.from_pretrained(pretrained_name, add_prefix_space=True)
    model = AutoModelForSequenceClassification.from_pretrained(pretrained_name, num_labels=3)
    model.to('cuda')
    
    tok = lambda input_sentence: tokenizer(input_sentence, max_length=20, padding='max_length', truncation=True) #tokenizer function
    
    #get data in correct form
    companies = ['Google', 'Microsoft', 'Tesla']
    all_tweets = [] #list of tweets
    labels = [] #list of labels (0 for Google, 1 for Microsoft, 2 for Tesla)
    for index, company in enumerate(companies):
        tweets = pd.read_csv(f'{company}.csv')['Content'].to_list() #read tweets in csv file
        tweets = [re.sub(company, '[MASK]', tweet, re.I) for tweet in tweets] #remove company name from tweets
        tweets = [tok(tweet) for tweet in tweets] #tokenize tweets
        all_tweets += tweets #add tweets to big list of tweets
        
        #add equally long and aligned list of indeces (labels) to label list
        length = len(tweets)
        labels += [index] * length
    
    #shuffle the lists and make sure they stay aligned
    temp = list(zip(all_tweets, labels))
    random.shuffle(temp)
    all_tweets, labels = zip(*temp)
    all_tweets, labels = list(all_tweets), list(labels)
    
    #get integer corresponding to 90% of the way through the dataset (for train-valid split)
    length = len(all_tweets)
    ninety = int(length * 0.9)
    
    #put data in its final form
    train = [{'input_ids': all_tweets[i]['input_ids'], 'labels': labels[i]} for i, _ in enumerate(all_tweets[:ninety])]
    validation = [{'input_ids': all_tweets[i]['input_ids'], 'labels': labels[i]} for i, _ in enumerate(all_tweets[ninety:])]
    
    #initialize training arguments/hyperparameters
    training_args = TrainingArguments(
        output_dir='test_trainer', 
        evaluation_strategy='epoch', 
        num_train_epochs=5,
        save_steps=10000,
        learning_rate = 0.01
    )
    
    #define the trainer
    trainer = Trainer(
        model = model,
        args = training_args,
        train_dataset=train,
        eval_dataset=validation,
    )
    
    #train
    trainer.train()
    
    #save model
    save_directory = './model_save'
    tokenizer.save_pretrained(save_directory)
    model.save_pretrained(save_directory)
    
if __name__ == '__main__':
    main()