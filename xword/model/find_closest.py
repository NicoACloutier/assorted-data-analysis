import pandas as pd
import numpy as np
import gensim
import re

def delete_punctuation(string: str) -> str:
    '''
    Delete punctuation from string
    '''
    return ''.join(char for char in string if char not in string.punctuation)

def clean(text: str) -> str:
    '''
    Remove stopwords from text, put in lowercase, and delete punctuation
    '''
    text = f' {text} '
    text = delete_punctuation(text.lower())
    for stopword in nltk.corpus.stopwords.words('english'):
        text = text.replace(f' {stopword} ', ' ')
    return text

def filter_df(df: pd.DataFrame, length: int, filled_in: str) -> pd.DataFrame:
    '''
    Filter values in a `DataFrame` to those of a particular length satisfying a particular filled in string.
    '''
    df = df[df['Answer'].apply(len) == length]
    fulfill_string_list = [re.match(filled_in, answer) for answer in list(df['Answer'])]
    df = df[fulfill_string_list]
    return df

def find_rep(clue: str, model: gensim.models.Word2Vec) -> np.ndarray:
    return np.mean([model.wv[word] for word in clue.split()])

def find_closest(length: int, filled_in: str, clue: str, model: gensim.models.Word2Vec, n: int, df: pd.DataFrame) -> np.ndarray:
    '''
    Find the `n` closest words.
    '''
    clue = clean(clue)
    df = filter_df(df, length, filled_in)
    representation = find_rep(clue, model)
    clue_representations = np.array([find_rep(temp_clue, model) for temp_clue in df['Clue']])
    rankings = sorted(np.linalg.norm(clue_representations - representation, axis=1))
    return rankings[n:]