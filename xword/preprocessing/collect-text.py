import nltk
from nltk.corpus import webtext, gutenberg
import unidecode
import random
import pandas as pd

#This script collects text data to pretrain the masked language model.
#It goes through a list of corpora and gets a list of words with another word that appears in the environment.

PROPORTION = 0.9 #proportion of characters in text obscured
MAX_LENGTH = 25 #maximum length of answer & clue strings
DATA_DIR = '..\\data'

replace_character = lambda char, proportion: char if random.random() >= proportion else '_' #randomly replace character with '_' a certain proportion of the time
cutoff = lambda string: string if len(string) <= MAX_LENGTH else string[:MAX_LENGTH] #cutoff string if greater than max length

#remove stopwords from text
def remove_stopwords(text):
    for stopword in nltk.corpus.stopwords.words('english'):
        text = text.replace(f' {stopword} ', ' ')
    return text

#ensure a number is within a given minimum and maximum
def within_range(number, minimum, maximum):
    number = minimum if number < minimum else number
    number = maximum if number > maximum else number
    return number

#get a random word within another word's environment
def get_environment_word(wordlist, index, minimum, maximum):
    environment_change = random.randint(1, 4) #how many words forwards or backwards the environment
    environment_change *= random.choice([-1, 1]) #chosse whether it will go forwards or backwards
    environment_index = within_range(index + environment_change,
                                     minimum, maximum) #index of word in this word's environment, ensured within range
    environment_word = wordlist[environment_index]
    return environment_word

#randomly replace a proportion of the characters in a string with '_'.
def obscure(string, proportion):
    string = [replace_character(char, proportion) for char in string]
    string = ''.join(string)
    return string

#put together all texts within an nltk corpus
def collect_corpus(corpus):
    corpus_text = ''
    filenames = corpus.fileids()
    for filename in filenames:
        corpus_text += ' ' + corpus.raw(filename)
    corpus_text = unidecode.unidecode(corpus_text)
    corpus_text = corpus_text.lower()
    return corpus_text

def main():
    nltk.download('webtext')
    nltk.download('gutenberg')
    word_dictionaries = []

    #create large text with all files in corpus
    all_text = ''
    corpora = [webtext, gutenberg]
    for corpus in corpora:
        all_text += ' ' + collect_corpus(corpus)
    all_text = remove_stopwords(all_text)
    
    words = all_text.split()
    length = len(words)
    for (i, word) in enumerate(words):
        env_word = get_environment_word(words, i, 0, length-1)
        env_word, word = cutoff(env_word), cutoff(word) #make sure they are below maximum length
        obscured_word = obscure(word, PROPORTION) #replace certain proportion of word with '_'
        word_dictionaries.append({'Answer': word, 'Obscured': obscured_word, 'Clue': env_word})
    
    df = pd.DataFrame(word_dictionaries)
    df.to_csv(f'{DATA_DIR}\\text.csv', index=False)

if __name__ == '__main__':
    main()