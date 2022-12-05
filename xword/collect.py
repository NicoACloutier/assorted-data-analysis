import pandas as pd
from selenium import webdriver
import re
import json

#Collect the 

WEBDRIVER_DIR = 'C:\\Users\\nicoc\\Documents\\chromedriver'
REPO_URL = 'https://github.com/doshea/nyt_crosswords'

remove = lambda x: re.sub('^[0-9]+?\. ', '', x) #remove the initial numbers

#parse an xword json in a particular direction
def parse(json_dict, direction):
    answer_dict = dict()
    answers = json_dict['answers'][direction]
    clues = json_dict['clues'][direction]
    clues = [remove(clue) for clue in clues]
    for (i, clue) in enumerate(clues):
        answer_dict[clue] = answers[i]
    return answer_dict

def main():
    driver = webdriver.Chrome(executable_path=WEBDRIVER_DIR)
    
    driver.get(REPO_URL)
    driver.quit()

if __name__ == '__main__':
    main()
