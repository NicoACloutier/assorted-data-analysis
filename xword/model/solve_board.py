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

def is_across_word_start(representation: str, current_char: int, line_length: int) -> bool:
    '''
    Check whether a representation index is the start of an across word.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `current_char: int`: the index of the current character.
        `line_length: int`: how long a line is on this board in characters.
    Returns:
        `bool`: whether the character is the start of an across word.
    '''
    if current_char >= len(representation):
        return False
    else:
        return current_char % line_length == 0 or representation[current_char-1] == '!'
    

def is_down_word_start(representation: str, current_char: int, line_length: int) -> bool:
    '''
    Check whether a representation index is the start of a down word.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `current_char: int`: the index of the current character.
        `line_length: int`: how long a line is on this board in characters.
    Returns:
        `bool`: whether the character is the start of a down word.
    '''
    if current_char >= len(representation):
        return False
    else:
        return current_char < line_length or representation[current_char-line_length] == '!'

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
    while num_count != number and current_char != len(representation):
        if (representation[current_char] not in ['!', '\n']) and (is_across_word_start(representation, current_char, line_length) or is_down_word_start(representation, current_char, line_length)):
            num_count += 1
        current_char += 1
    return current_char

def filter_wordlist(word_rep: str, wordlist: list[str]) -> list[str]:
    '''
    Filter a wordlist given a word representation pattern.
    Arguments:
        `word_rep: str`: the word representation pattern.
        `wordlist: list[str]`: a list of possible words given as answers.
    Returns:
        `list[str]`: a list of words that fit the pattern.
    '''
    wordlist = [word for word in wordlist if len(word) == len(word_rep)]
    for i, char in enumerate(word_rep):
        if char != '_':
            wordlist = [word for word in wordlist if word[i] == char]
    return wordlist

def find_word_rep(representation: str, index: int, across: bool, line_length: int) -> str:
    '''
    Find the representation of a word if its index is already known.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `index: int`: the index of the word in the board representation.
        `across: bool`: whether the word goes across.
        `line_length: int`: the length of a line.
    Returns:
        `str`: the representation of the word alone.
    '''
    word_rep = ''
    while index < len(representation) and representation[index] != '!':
        word_rep += representation[index]
        index += 1 if across else line_length
    return word_rep

def find_number_info(representation: str, number: int, across: bool) -> str:
    '''
    Find a word place within a crossword representation string.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `number: int`: the number of the word.
        `across: bool`: whether the word goes across.
    Returns:
        `str`: the representation of the word alone.
    '''
    word_rep = ''
    line_length = representation.index('\n')
    representation = representation.replace('\n', '')
    current_char = find_rep_index(representation, number, line_length)
    return find_word_rep(representation, current_char, across, line_length)

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
    item_counter = collections.Counter([wordlist[ind] for ind in nearest])
    word = max([wordlist[ind] for ind in nearest], key=item_counter.get)
    return word if item_counter[word] > 1 else None, item_counter[word]

def change_rep(representation: str, numbers: list[int], i: int, line_length: int, across: bool) -> tuple[str, bool, int]:
    '''
    Change the representation string, ensuring no changes are made that conflict with past changes.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `numbers: list[int]`: the list of numbers in the prompt list
        `i: int`: the index of the prompt in the prompt list.
        `line_length: int`: the length of a line.
        `across: bool`: whether the word goes across.
    Returns:
        `str`: the updated representation string.
        `bool`: whether the string was replaced successfully.
        `int`: the number of the word.
    '''
    char_index = find_rep_index(representation, numbers[i], line_length)
    word = find_word_rep(representation, char_index, across, line_length)
    bad = False
    for char in word:
        if representation[char_index] not in ['_', '!'] + [char,]:
            bad = True
            break
    if bad:
        return representation, not bad, numbers[i]
    char_index -= len(word)
    for char in word:
        representation = representation[:char_index] + char + representation[char_index+1:]
        char_index += 1 if across else line_length
    return representation, not bad, numbers[i]

def model_fill(clue: str, clue_list: list[str]) -> str:
    '''
    Probabalistically fill unfilled characters in a clue given a prompt list.
    Arguments:
        `clue: str`: the clue as it currently is, with letters not yet filled in.
        `clue_list: list[str]`: the list of representations of clues.
    Returns:
        `str`: the filled prompt.
    '''
    temp_prompt_list = [re.search(clue.replace('_', '.'), prompt) for prompt in clue_list]
    temp_prompt_list = [prompt.group(0) for prompt in temp_prompt_list if prompt]
    if len(temp_prompt_list) == 0:
        clue1, clue2 = clue[:len(clue)//2], clue[len(clue)//2:]
        return model_fill(clue1, clue_list) + model_fill(clue2, clue_list)
    for i, char in enumerate(clue):
        if char == '_':
            char_list = [prompt[i] for prompt in temp_prompt_list]
            char_counter = collections.Counter(char_list)
            clue[i] = max(char_counter, key=lambda x: char_counter[x])
    return clue

def update_rep(representation: str, current_char: int, wordlist: list[str], answers: dict[int, str], prompts: dict[int, str],
               number: int, across: bool, line_length: int) -> tuple[dict[int, str], dict[int, str], str]:
    '''
    Update a representation for patterns with only one possibility in the reference corpus.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `current_char: int`: the index of the current character within the representation.
        `wordlist: list[str]`: a list of possible words given as answers.
        `answers: dict[int, str]`: the answers.
        `prompts: dict[int, str]`: the prompts.
        `number: int`: the number of a word in the representation.
        `across: bool`: whether the word goes across.
        `line_length: int`: the length of a line.
    Returns:
        `dict[int, str]`: the updated prompts.
        `dict[int, str]`: the updates answers.
        `str`: the updated representation.
    '''
    word_rep = ''
    while current_char < len(representation) and representation[current_char] != '!':
        word_rep += representation[current_char]
        current_char += 1 if across else line_length
    current_char -= len(word_rep) * (1 if across else line_length)
    if '_' in word_rep:
        possibilities = list(set(filter_wordlist(word_rep, wordlist)))
        if len(possibilities) == 1:
            answers[number] = possibilities[0]
            del prompts[number]
            for i, char in enumerate(possibilities[0]):
                index = current_char + i * (1 if across else line_length)
                representation = representation[index:] + char + representation[index+1:]
    return prompts, answers, representation

def filter_unique(representation: str, wordlist: list[str], down_prompts: dict[int, str], across_prompts: dict[int, str], 
                  down_answers: dict[int, str], across_answers: dict[int, str]) -> tuple[dict[int, str], dict[int, str], dict[int, str], dict[int, str], str]:
    '''
    Filter out words with unique possible answers given the reference list and update answers and representation accordingly.
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `wordlist: list[str]`: a list of possible words given as answers.
        `across_prompts: dict[int, str]`: the prompts going down.
        `down_prompts: dict[int, str]`: the prompts going across.
        `across_answers: dict[int, str]`: the answers going down.
        `down_answers: dict[int, str]`: the answers going across.
    Returns:
        `dict[int, str]`: the updated down answers.
        `dict[int, str]`: the updated across answers.
        `dict[int, str]`: the updated down prompts.
        `dict[int, str]`: the updated across prompts.
        `str`: the updated representation.
    '''
    line_length, temp_rep = representation.index('\n'), representation.replace('\n', '')
    number = 0
    for i, char in enumerate(representation):
        across_word, down_word = is_across_word_start(temp_rep, i, line_length), is_down_word_start(temp_rep, i, line_length)
        number += int(across_word or down_word)
        if char != '!' and across_word:
            across_prompts, across_answers, temp_rep = update_rep(temp_rep, i, wordlist, across_prompts, across_answers, number, True, line_length)
        if char != '!' and down_word:
            down_prompts, down_answers, temp_rep = update_rep(temp_rep, i, wordlist, down_prompts, down_answers, number, False, line_length)
    for i in range(1, len(temp_rep)//line_length):
        temp_rep = temp_rep[i*line_length+i:] + '\n' + temp_rep[:i*line_length+i]
    representation = temp_rep
    return down_answers, across_answers, down_prompts, across_prompts, representation

def get_none(representation: str, wordlist: list[str], down_prompts: dict[int, str], across_prompts: dict[int, str]) -> tuple[dict[int, str], dict[int, str], dict[int, str], dict[int, str]]:
    '''
    Arguments:
        `representation: str`: the string representation of a crossword board.
        `wordlist: list[str]`: a list of possible words given as answers.
        `down_prompts: dict[int, str]`: the prompts going down, with numbers.
        `across_prompts: dict[int, str]`: the prompts going across, with numbers.
    Returns:
        `dict[int, str]`: the nones going down.
        `dict[int, str]`: the nones going across.
        `dict[int, str]`: the updated prompts going down.
        `dict[int, str]`: the updates prompts going across.
    '''
    across_nones, down_nones = dict(), dict()
    line_length, temp_rep = representation.index('\n'), representation.replace('\n', '')
    print(representation)
    print(line_length)
    number = 0
    for i, char in enumerate(representation):
        across_word, down_word = is_across_word_start(temp_rep, i, line_length), is_down_word_start(temp_rep, i, line_length)
        number += int(across_word or down_word)
        if char != '!' and across_word:
            if len(filter_wordlist(find_number_info(representation, number, True), wordlist)) == 0 and number in across_prompts:
                across_nones[number] = across_prompts[number]
                del across_prompts[number]
        if char != '!' and down_word:
            if len(filter_wordlist(find_number_info(representation, number, False), wordlist)) == 0 and number in down_prompts:
                down_nones[number] = down_prompts[number]
                del down_promts[number]
    return down_nones, across_nones, down_prompts, across_prompts

def get_closest_words(representation: str, down_prompts: dict[int, str], across_prompts: dict[int, str], wordlist: list[str], 
                        across_answers: dict[int, str], down_answers: dict[int, str]) -> tuple[dict[int, str], dict[int, str], dict[int, str], dict[int, str], str]:
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
        `dict[int, str]`: the updated answers down.
        `dict[int, str]`: the updated answers across.
        `str`: the updated representation string.
    '''
    line_length = representation.index('\n')
    down_numbers, across_numbers = list(down_prompts.keys()), list(across_prompts.keys())
    across_clues = [find_number_info(representation, number, True) for number in across_prompts]
    down_clues = [find_number_info(representation, number, False) for number in down_prompts]
    model = sentence_transformers.SentenceTransformer(MODEL)
    with open(EMBED_FILE, 'rb') as f:
        embeddings = pickle.loads(f.read())
    across_answers = {clue: find_closest(model, clue, wordlist, embeddings) for clue in across_clues}
    down_answers = {clue: find_closest(model, clue, wordlist, embeddings) for clue in down_clues}
    for x in range(1, NUM_WORDS+1)[::-1]:
        temp_across_answers = [answer for answer in across_answers if across_answers[answer][1] == x]
        temp_down_answers = [answer for answer in down_answers if down_answers[answer][1] == x]
        for i, word in enumerate(temp_down_answers):
            representation, good, number = change_rep(representation, down_numbers, i, line_length, False)
            if good:
                down_answers[number] = word
                del down_prompts[number]
        for i, word in enumerate(temp_across_answers):
            representation, good, number = change_rep(representation, across_numbers, i, line_length, True)
            if good:
                across_answers[number] = word
                del across_prompts[number]
    return down_answers, across_answers, down_prompts, across_prompts, representation

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
    print(representation)
    df = pd.read_csv('../data/xword.csv')
    wordlist = list(df['Answer'].astype(str))
    previous_length, current_length, none_list = -1, 0, []
    down_answers, across_answers = dict(), dict()
    while (down_prompts or across_prompts) and current_length != previous_length:
        print(representation)
        down_answers, across_answers, down_prompts, across_prompts, representation = get_closest_words(representation, down_prompts, across_prompts, wordlist, down_answers, across_answers)
        print(representation)
        down_answers, across_answers, down_prompts, across_prompts, representation = filter_unique(representation, wordlist, down_prompts, across_prompts, down_answers, across_answers)
        down_nones, across_nones, down_prompts, across_prompts = get_none(representation, wordlist, down_prompts, across_prompts)
        previous_length = current_length
        current_length = len(down_answers) + len(across_answers)
    print(representation)
    for prompt in down_nones:
        down_prompts[prompt] = down_nones[prompt]
    for prompt in across_prompts:
        across_prompts[prompt] = across_nones[prompt]
    if down_prompts or across_prompts:
        representation, down_answers, across_answers = model_fill(representation, wordlist)
    return down_answers, across_answers