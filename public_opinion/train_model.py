from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import numpy as np
import pandas as pd
import torch
import random
import re

pretrained_name = 'facebook/bart-large-mnli'
tokenizer = AutoTokenizer.from_pretrained(pretrained_name, add_prefix_space=True)
model = AutoModelForSequenceClassification.from_pretrained(pretrained_name, num_labels=3)
model.to('cuda')

tok = lambda input_sentence: tokenizer(input_sentence, max_length=20, padding='max_length', truncation=True)

companies = ['Google', 'Microsoft', 'Tesla']
all_tweets = []
labels = []
for index, company in enumerate(companies):
    tweets = pd.read_csv(f'{company}.csv')['Content'].to_list()
    tweets = [re.sub(company, '', tweet, re.I) for tweet in tweets]
    tweets = [tok(tweet) for tweet in tweets]
    all_tweets += tweets
    length = len(tweets)
    labels += [index] * length

temp = list(zip(all_tweets, labels))
random.shuffle(temp)
all_tweets, labels = zip(*temp)
all_tweets, labels = list(all_tweets), list(labels)

length = len(all_tweets)
ninety = int(length * 0.9)

train = [{'input_ids': all_tweets[i]['input_ids'], 'labels': labels[i]} for i, _ in enumerate(all_tweets[:ninety])]
validation = [{'input_ids': all_tweets[i]['input_ids'], 'labels': labels[i]} for i, _ in enumerate(all_tweets[ninety:])]

training_args = TrainingArguments(
    output_dir='test_trainer', 
    evaluation_strategy='epoch', 
    num_train_epochs=3,
    save_steps=10000,
    learning_rate = 0.01
)

trainer = Trainer(
    model = model,
    args = training_args,
    train_dataset=train,
    eval_dataset=validation,
)

trainer.train()

save_directory = './model_save'
tokenizer.save_pretrained(save_directory)
model.save_pretrained(save_directory)