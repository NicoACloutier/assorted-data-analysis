import pandas as pd
import collections
from unidecode import unidecode
import random

#This script removes non-unicode characters, puts the text in lowercase, and makes sure the 
#answers and clues are all at most MAX_LENGTH characters long. It also adds a new column
#that will be an input column for the model with a certain proportion of characters in a string replaced with '_'.
#It does this several times, obscuring a different proportion of the data each time.

MAX_LENGTH = 20 #maximum length of answers/clues
DATA_DIR = '..\\data'
PROPORTIONS = [0.8, 0.5, 0.25, 0.1] #proportion of characters in answers that will be obscured
TIMES_AUGMENTED = 3 #how many times each column should appear in the augmented dataset

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
    
    test_df = df.sample(frac=0.1)
    df = df.drop(test_df.index)
    
    #obscure different proportions of the answer
    dataframes = []
    for proportion in PROPORTIONS:
        temp_df = df.copy()
        temp_df['Obscured'] = temp_df['Answer'].apply(lambda x: obscure(x, proportion))
        dataframes.append(temp_df)
    
    df = pd.concat(dataframes)
    df = df.sample(frac=1)
    
    test_dataframes = []
    for proportion in PROPORTIONS:
        temp_df = test_df.copy()
        temp_df['Obscured'] = temp_df['Answer'].apply(lambda x: obscure(x, proportion))
        test_dataframes.append(temp_df)
    
    test_df = pd.concat(test_dataframes)
    test_df = test_df.sample(frac=1)
    
    df.to_csv(f'{DATA_DIR}\\train.csv', index=False)
    test_df.to_csv(f'{DATA_DIR}\\test.csv', index=False)

if __name__ == '__main__':
    main()
