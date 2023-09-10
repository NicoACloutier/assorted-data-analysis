import sentence_transformers, nltk
import string, pickle, collections, typing
import pandas as pd
import numpy as np

MODEL = 'bert-base-uncased'
DATA_FILE = '../data/xword.csv'
EMBED_FILE = '../data/embeddings'
NUM_WORDS = 5

def delete_punctuation(input_string: str) -> str:
    '''
    Delete the punctuation from a string.
    Arguments:
        `input_string: str`: the string to be changed.
    Returns:
        `str`: the string without punctuation.
    '''
    return ''.join(char for char in input_string if char not in string.punctuation)

def find_closest(model: sentence_transformers.SentenceTransformer, clue: str, wordlists: list[str], embeddings: np.ndarray) -> typing.Optional[str]:
    '''
    Find the closest embeddings to a given prompt. Finds `NUM_WORDS` closest. If multiple are the same string, return string. Otherwise, return `None`.
    Arguments:
        `model: sentence_transformers.SentenceTransformer`: the sentence transformer model used for embedding generation.
        `clue: str`: the word clue in string form.
        `wordlists: str`: the list of words in the references.
        `embeddings: np.ndarray`: the pre-generated embeddings for the prompts in 
    Returns:
        `typing.Optional[str]`: the found string if multiple among `NUM_WORDS` are the same. Otherwise, `None`.
    '''
    embedding = model.encode(clue)
    nearest = np.linalg.norm(embeddings - embedding, axis=1).argsort()[:NUM_WORDS]
    item_counter = collections.Counter([wordlists[ind] for ind in nearest])
    word = max([wordlists[ind] for ind in nearest], key=item_counter.get)
    return word if item_counter[word] > 1 else None

def solve_board(representation: str, down_prompts: dict[int, str], across_prompts: dict[int, str]) -> tuple[dict[int, str], dict[int, str]]:
    '''
    Solve a crossword board.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `down_prompts: dict[int, str]`: the prompts going down, with numbers.
        `across_prompts: dict[int, str]`: the prompts going across, with numbers.
    Returns:
        `dict[int, str]`: the answers going down.
        `dict[int, str]`: the answers going across.
    '''
    wordlist = list(df['Answer'].astype(str))
    previous_length, current_length, none_list = -1, 0, []
    while (down_prompts or across_prompts) and current_length != previous_length:
        down_answers, across_answers, representation = get_closest_words(representation, down_prompts, across_prompts, wordlist) #TODO
        down_answers, across_answers, representation = filter_unique(representation, wordlist) #TODO
        none_list, down_prompts, across_prompts = get_none(representation, wordlist, down_prompts, across_prompts) #TODO
        previous_length = current_length
        current_length = len(down_answers) + len(across_answers)
    down_prompts, across_prompts = repopulate_prompts(none_list) #TODO
    if down_prompts or across_prompts:
        representation, down_answers, across_answers = model_fill(representation, down_prompts, across_prompts) #TODO
    return down_answers, across_answers