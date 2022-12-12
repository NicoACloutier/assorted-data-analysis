import torch
from torch import nn
from torch.nn import functional as F
from gensim.models import Word2Vec
import pandas as pd

#This script trains the model

MAX_LENGTH = 25

convert_to_matrix = lambda word, letter_vectors: [letter_vectors[letter] for letter in word] #convert word to matrix
fill_out = lambda word, max_length: word + ' ' * (max_length - len(word)) #add spaces until a word is 25 characters long

def main():
    letter_vectors = Word2Vec.load('..\\preprocessing\\word2vec.model') #load word2vec model
    model = nn.Transformer(d_model=10, nhead=5) #initialize transformer model
    df = pd.read_csv('..\\data\\text.csv') #load data
    
    #fill clues and answers to max length
    df['Clue'] = df['Clue'].apply(lambda x: fill_out(x, MAX_LENGTH))
    df['Answer'] = df['Answer'].apply(lambda x: fill_out(x, MAX_LENGTH))
    
    #train/test split
    train_df = df.sample(frac=0.9)
    test_df = df.drop(train.index)

    #get vectors for words
    train_source = [convert_to_matrix(row['Clue'], letter_vectors.wv) for row in train_df.iterrows()]
    train_target = [convert_to_matrix(row['Answer'], letter_vectors.wv) for row in train_df.iterrows()]
    test_source = [convert_to_matrix(row['Clue'], letter_vectors.wv) for row in test_df.iterrows()]
    test_target = [convert_to_matrix(row['Answer'], letter_vectors.wv) for row in test_df.iterrows()]

    #convert data to pytorch tensors
    train_source = torch.as_tensor(train_source)
    train_target = torch.as_tensor(train_target)
    test_source = torch.as_tensor(test_source)
    test_target = torch.as_tensor(test_target)

if __name__ == '__main__':
    main()