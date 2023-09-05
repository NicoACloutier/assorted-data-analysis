import sentence_transformers, nltk
import string, pickle
import pandas as pd
import numpy as np

MODEL = 'bert-base-uncased'
DATA_FILE = '../data/xword.csv'
EMBED_FILE = '../data/embeddings'
TEST_WORDS = {'____': 'Capital city near the Nile Delta.'}

def delete_punctuation(input_string):
    return ''.join(char for char in input_string if char not in string.punctuation)

def clean(text):
    text = f' {text} '
    text = delete_punctuation(text.lower())
    for stopword in nltk.corpus.stopwords.words('english'):
        text = text.replace(f' {stopword} ', ' ')
    return text

def find_closest(model, clue, wordlists, embeddings):
    embedding = model.encode(clue)
    nearest = np.argmin(np.linalg.norm(embeddings - embedding))
    return wordlists[nearest]

def main():
    df = pd.read_csv(DATA_FILE)
    model = sentence_transformers.SentenceTransformer(MODEL)
    with open(EMBED_FILE, 'rb') as f:
        embeddings = pickle.loads(f.read())
    for test_word in TEST_WORDS:
        find_closest(model, TEST_WORDS[test_word], list(df['Clue']), embeddings)

if __name__ == '__main__':
    main()