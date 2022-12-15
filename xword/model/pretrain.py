import torch
from torch import nn
from torch.nn import functional as F
from gensim.models import Word2Vec
import pandas as pd
import time
import functools
import numpy as np

#This script pretrains the model on raw text data.

MAX_LENGTH = 20
BATCH_SIZE = 500
LEARNING_RATE = 0.01
NUM_EPOCHS = 1
letter_vectors = Word2Vec.load('..\\preprocessing\\word2vec.model') #load word2vec model

fill_out = lambda word, max_length: word + ' ' * (max_length - len(word)) #add spaces until a word is 25 characters long

#convert word to matrix
@functools.cache
def convert_to_matrix(word):
    return [letter_vectors.wv[letter] for letter in word]

#find the input word matrices for a list of rows from the dataframe
def find_word_matrices(dict_list):
    word_matrices = [convert_to_matrix(row['Clue']) + convert_to_matrix(row['Obscured']) for row in dict_list]
    return word_matrices

#remove forbidden characters from a string
def clean_string(string, forbidden_chars):
    for char in forbidden_chars:
        string = string.replace(char, '')
    return string

#change number of elapsed seconds to string
def secs_to_str(seconds_elapsed):
    if seconds_elapsed < 60:
        return f'{seconds_elapsed:.3f} seconds'
    elif seconds_elapsed > 60:
        return f'{seconds_elapsed/60:.3f} minutes'
    else:
        return '1 minute'

def main():
    start = time.time()
    model = nn.Transformer(d_model=10, nhead=5) #initialize transformer model
    df = pd.read_csv('..\\data\\text.csv') #load data
    df = df.astype(str)
    
    #remove characters not in the word2vec model
    text = ''.join(list(df['Clue'])) + ''.join(list(df['Answer']))
    chars = list(set(text))
    forbidden_chars = [char for char in chars if char not in letter_vectors.wv]
    df['Clue'] = df['Clue'].apply(lambda x: clean_string(x, forbidden_chars))
    df['Answer'] = df['Answer'].apply(lambda x: clean_string(x, forbidden_chars))
    df['Obscured'] = df['Obscured'].apply(lambda x: clean_string(x, forbidden_chars))
    
    #fill clues and answers to max length
    df['Clue'] = df['Clue'].apply(lambda x: fill_out(x, MAX_LENGTH))
    df['Answer'] = df['Answer'].apply(lambda x: fill_out(x, MAX_LENGTH))
    df['Obscured'] = df['Obscured'].apply(lambda x: fill_out(x, MAX_LENGTH))
    
    #train/test split
    train_df = df.sample(frac=0.9)
    test_df = df.drop(train_df.index)
    
    end = time.time()
    print(f'Completed data and model loading in {secs_to_str(end-start)}.')

    clean_start = time.time()
    #get vectors for words
    train_dicts = [row for _, row in train_df.iterrows()]
    test_dicts = [row for _, row in test_df.iterrows()]
    end = time.time()
    print(f'Finished making dictionary lists in {secs_to_str(end-clean_start)}.')
    
    start = time.time()
    train_source = [convert_to_matrix(row['Clue']) + convert_to_matrix(row['Obscured']) for row in train_dicts]
    end = time.time()
    print(f'Finished train source in {secs_to_str(end-start)}.')
    
    start = time.time()
    train_target = [convert_to_matrix(row['Answer']) for row in train_dicts]
    end = time.time()
    print(f'Finished train target in {secs_to_str(end-start)}.')
    
    start = time.time()
    test_source = [convert_to_matrix(row['Clue']) + convert_to_matrix(row['Obscured']) for row in test_dicts]
    end = time.time()
    print(f'Finished test source in {secs_to_str(end-start)}.')
    
    start = time.time()
    test_target = [convert_to_matrix(row['Answer']) for row in test_dicts]
    end = time.time()
    print(f'Finished test target in {secs_to_str(end-start)}.')

    #convert data to pytorch tensors
    train_source = torch.as_tensor(np.array(train_source))
    train_target = torch.as_tensor(np.array(train_target))
    test_source = torch.as_tensor(np.array(test_source))
    test_target = torch.as_tensor(np.array(test_target))
    
    clean_end = time.time()
    print(f'Finished data cleaning in {secs_to_str(clean_end-clean_start)}.')
    
    train_length = len(train_source)
    test_length = len(test_source)
    num_batches = train_length // BATCH_SIZE
    test_batch_size = test_length // num_batches
    
    criterion = nn.MSELoss() 
    optimizer = torch.optim.SGD(model.parameters(), lr=LEARNING_RATE) 
    
    for epoch in range(NUM_EPOCHS):
        print(f'\nEPOCH {epoch+1}\n') 
        total_loss = 0 
        start = time.time() 
        for (i, sequence) in enumerate(train_source):
            target = train_target[i]
            output = model.forward(sequence, target)
            loss = criterion(output, target)
            loss.backward() 
            optimizer.step() 
            optimizer.zero_grad()
            total_loss += loss #add loss to total loss
            
            if (i+1) % BATCH_SIZE == 0:
            
                #the following code is to see how well the model is doing on the validation data
                step = (i+1) // BATCH_SIZE 
                beginning_value = test_batch_size * (step-1) #the first value of the test data to be used for this batch
                ending_value = test_batch_size * (step) #the last value of the test data to be used for this batch
                temp_seq = test_source[beginning_value:ending_value] 
                temp_targ = test_target[beginning_value:ending_value] 
                valid_loss = 0 #set the total validation loss equal to 0
                
                for (ind, test_seq) in enumerate(temp_seq):
                    test_targ = temp_targ[ind]
                    output = model.forward(test_seq, test_targ)
                    loss = criterion(output, test_targ)
                    valid_loss += loss #add loss to total
                avg_valid_loss = valid_loss / len(temp_seq)
                
                avg_loss = total_loss / BATCH_SIZE
                total_loss = 0
                end = time.time()
                elapsed = end - start
                print(f'Iteration number {i+1}.	Loss: {avg_loss:.3f}.	Time: {secs_to_str(elapsed)}. Validation loss: {avg_valid_loss:.3f}') #report
                start = time.time() #reset start time
    
    torch.save(model, 'saves\\pretrained.pt') #save model to local directory

if __name__ == '__main__':
    main()