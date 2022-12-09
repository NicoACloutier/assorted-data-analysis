import pandas as pd
import collections
from unidecode import unidecode
import random

#This script removes non-unicode characters, puts the text in lowercase, and makes sure the 
#answers and clues are all at most MAX_LENGTH characters long. It also adds a new column
#that will be an input column for the model with a certain proportion of characters in a string replaced with '_'

MAX_LENGTH = 25 #maximum length of answers/clues
DATA_DIR = '..\\data'
PROPORTION = 0.9 #proportion of characters in answers that will be obscured

cutoff = lambda string: string if len(string) <= MAX_LENGTH else string[:MAX_LENGTH] #cutoff string if greater than max length
replace_character = lambda char, proportion: char if random.random() >= proportion else '_' #randomly replace character with '_' a certain proportion of the time

#randomly replace a proportion of the characters in a string with '_'.
def obscure(string, proportion):
    string = [replace_character(char, proportion) for char in string]
    string = ''.join(string)
    return string

def main():
    df = pd.read_csv(f'{DATA_DIR}\\xword.csv')
    df['Clue'] = df['Clue'].astype(str).apply(unidecode) #remove diacritics
    df['Answer'] = df['Answer'].astype(str).apply(unidecode) #remove diacritics
    df['Clue'] = df['Clue'].apply(lambda x: x.lower())
    df['Answer'] = df['Answer'].apply(lambda x: x.lower())
    df['Clue'] = df['Clue'].apply(cutoff)
    df['Answer'] = df['Answer'].apply(cutoff)
    
    df['KnownLetters'] = df['Answer'].apply(lambda x: obscure(x, PROPORTION))
    df['Length'] = df['Answer'].apply(len)
    
    df.to_csv(f'{DATA_DIR}\\xword-clean.csv', index=False)

if __name__ == '__main__':
    main()
