import sentence_transformers, nltk
import string, pickle
import pandas as pd
import numpy as np

MODEL = 'bert-base-uncased'
DATA_FILE = '../data/xword.csv'
OUT_FILE = '../data/embeddings'

def delete_punctuation(input_string):
    return ''.join(char for char in input_string if char not in string.punctuation)

def clean(text):
    text = f' {text} '
    text = delete_punctuation(text.lower())
    for stopword in nltk.corpus.stopwords.words('english'):
        text = text.replace(f' {stopword} ', ' ')
    return text

def main():
    model = sentence_transformers.SentenceTransformer(MODEL)
    df = pd.read_csv(DATA_FILE)
    df['Clue'] = df['Clue'].apply(clean)
    thing = list(df['Clue'].apply(model.encode))
    with open(OUT_FILE, 'wb') as f:
        pickle.dump(thing, f)

if __name__ == '__main__':
    main()