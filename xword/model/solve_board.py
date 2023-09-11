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

def is_word_start(representation: str, current_char: int, line_length: int) -> bool:
    '''
    Check whether a representation index is the start of a word.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `current_char: int`: the index of the current character.
        `line_length: int`: how long a line is on this board in characters.
    Returns:
        `bool`: whether the character is the start of a word.
    '''
    return current_char % line_length == 0 or current_char < line_length or representation[current_char-1] == '!' or representation[current_char-line_length] == '!'

def find_rep_index(representation: str, number: int, line_length: int) -> int:
    '''
    Find the index of a number in a representation string.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `number: int`: the number of the word.
        `line_length: int`: the length of a line in the representation.
    Returns:
        `int`: the index of the number in the string.
    '''
    num_count, current_char = 0, 0
    while num_count != number:
        if (representation[current_char] not in ['!', '\n']) and is_word_start(representation, current_char, line_length):
            num_count += 1
        current_char += 1
    return current_char

def find_number_info(representation: str, number: int, down: bool) -> str:
    '''
    Find a word place within a crossword representation string.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `number: int`: the number of the word.
        `down: bool`: `False` if across, `True` if down.
    Returns:
        `str`: the representation of the word alone.
    '''
    word_rep = ''
    line_length = representation.index('\n')
    representation = representation.replace('\n', '')
    current_char = find_rep_index(representation, number, line_length)
    while current_char < len(representation) and representation[current_char] != '!':
        word_rep += representation[current_char]
        current_char += 1 if across else line_length
    return word_rep

def find_closest(model: sentence_transformers.SentenceTransformer, clue: str, wordlist: list[str], embeddings: np.ndarray) -> tuple[typing.Optional[str], int]:
    '''
    Find the closest embeddings to a given prompt. Finds `NUM_WORDS` closest. If multiple are the same string, return string. Otherwise, return `None`.
    Arguments:
        `model: sentence_transformers.SentenceTransformer`: the sentence transformer model used for embedding generation.
        `clue: str`: the word clue in string form.
        `wordlist: str`: the list of words in the references.
        `embeddings: np.ndarray`: the pre-generated embeddings for the prompts in 
    Returns:
        `typing.Optional[str]`: the found string if multiple among `NUM_WORDS` are the same. Otherwise, `None`.
        `int`: the number of words that were found that were the same.
    '''
    embedding = model.encode(clue)
    nearest = np.linalg.norm(embeddings - embedding, axis=1).argsort()[:NUM_WORDS]
    item_counter = collections.Counter([wordlists[ind] for ind in nearest])
    word = max([wordlists[ind] for ind in nearest], key=item_counter.get)
    return word if item_counter[word] > 1 else None, item_counter[word]

def change_rep(representation: str, numbers: list[int], i: int, line_length: int, across: bool) -> tuple[str, bool]:
    '''
    Change the representation string, ensuring no changes are made that conflict with past changes.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `numbers: list[int]`: the list of numbers in the prompt list
        `i: int`: the index of the prompt in the prompt list.
        `line_length: int`: the length of a line.
        `across: bool`: whether the word goes across
    Returns:
        `str`: the updated representation string.
        `bool`: whether the string was replaced successfully.
    '''
    char_index = find_rep_index(representation, numbers[i], line_length)
    bad = False
    for char in word:
        if representation[char_index] not in ['_', '!'] + char:
            bad = True
            break
    if bad:
        return representation
    char_index -= len(word)
    for char in word:
        representation[char_index] = char
        char_index += 1 if across else line_length
    return representation, !bad

def get_closest_words(representation: str, down_prompts: dict[int, str], across_prompts: dict[int, str], worldist: list[str], 
                        across_answers: dict[int, str], down_answers: dict[int, str]) -> tuple[dict[int, str], dict[int, str], str]:
    '''
    Perform the calculation of the closest words given prompts.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `down_prompts: dict[int, str]`: the prompts going down, with numbers.
        `across_prompts: dict[int, str]`: the prompts going across, with numbers.
        `wordlist: list[str]`: a list of possible words given as answers.
        `down_answers: dict[int, str]`: the answers going down.
        `across_answers: dict[int, str]`: the answers going across.
    Returns:
        `dict[int, str]`: the updated prompts down.
        `dict[int, str]`: the updated prompts across.
        `str`: the updated representation string.
    '''
    line_length = representation.index('\n')
    down_numbers, across_numbers = list(down_prompts.values()), list(across_prompts.values())
    across_clues = [find_number_info(representation, number, True) for number in across_prompts]
    down_clues = [find_number_info(representation, number, False) for number in down_prompts]
    model = sentence_transformers.SentenceTransformer(MODEL)
    with open(EMBED_FILE, 'rb') as f:
        embeddings = pickle.loads(f.read())
    across_answers = [find_closest(model, clue, wordlist, embeddings) for clue in across_clues]
    down_answers = [find_closest(model, clue, wordlist, embeddings) for clue in down_clues]
    for i in [x+1 for x in range(NUM_WORDS)][::-1]:
        temp_across_answers = [answer for answer in across_answers if answer[1] == i]
        temp_down_answers = [answer for answer in down_answers if answer[1] == i]
        for i, word in enumerate(temp_down_answers):
            representation, good = change_rep(representation, down_numbers, i, line_length, False)
            if good:
                down_answers[i] = word
                del down_prompts[i]
        for i, word in enumerate(temp_across_answers):
            representation, good = change_rep(representation, across_numbers, i, line_length, True)
            if good:
                across_answers[i] = word
                del across_prompts[i]
    return down_answers, across_answers, representation

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
        down_answers, across_answers, representation = get_closest_words(representation, down_prompts, across_prompts, wordlist)
        down_answers, across_answers, representation = filter_unique(representation, wordlist) #TODO
        none_list, down_prompts, across_prompts = get_none(representation, wordlist, down_prompts, across_prompts) #TODO
        previous_length = current_length
        current_length = len(down_answers) + len(across_answers)
    down_prompts, across_prompts = repopulate_prompts(none_list) #TODO
    if down_prompts or across_prompts:
        representation, down_answers, across_answers = model_fill(representation, down_prompts, across_prompts) #TODO
    return down_answers, across_answers