import pandas as pd
import selenium
from selenium import webdriver
import urllib
import numpy as np

driver = webdriver.Chrome()
URL = 'https://disc.gsfc.nasa.gov/datasets/M2I3NPASM_5.12.4/summary'
FRACTION = 10 #fraction of data to be kept, in form 1/FRACTION
DAYS_SURROUNDING = 4 #how many days surrounding the central day will be recorded on each side 
OUTPUT_FILE = '..\\data\\raw\\raw.csv'

#css selectors, name of variable is what button says
BUTTON_SELECTOR = '.btn.btn-xs.btn-link.borderless.pop.ng-scope'
DOWNLOAD_DROPDOWN_SELECTOR = 'panel.ng-isolate-scope.panel-default'
FILETYPE_SELECTOR = 'li.radio.ng-scope'
VARIABLE_DROPDOWN_SELECTOR = 'panel.ng-isolate-scope.panel-default'
DOWNLOAD_SELECTOR = 'download-button'

#parse the ascii text data from NASA data website
def parse_ascii(text):
    df = pd.DataFrame()
    text = text.split('\n')[1:] #first line just contains name of dataset, not useful
    for line in text:
        line = line.split(', ')
        (title, data) = (line[0], line[1:])
        df[title] = data
    return df

#split up a raw dataframe into a 3d np.ndarray
def split_up(df):
    array = df.to_numpy()
    array = np.resize(array, (array.size[0], (DAYS_SURROUNDING * 2) + 1, array.size[1]))
    return array

#turn the np.ndarray into dataframe with the proper number of columns
def to_df(array, start_columns):
    columns = []
    for i in range((DAYS_SURROUNDING * 2) + 1):
        columns += [f'{column}{i}' for column in start_columns]
    
    array = np.resize(array, (array.shape[0], array.shape[2]))
    
    df = pd.DataFrame(data=array, columns=columns)
    return df

def main():
    driver.get(URL)
    button_selectors = [BUTTON_SELECTOR, DOWNLOAD_DROPDOWN_SELECTOR, FILETYPE_SELECTOR, 
                        VARIABLE_DROPDOWN_SELECTOR, DOWNLOAD_SELECTOR] #TODO: finish collecting selectors
    for selector in button_selectors:
        driver.find_element_by_css_selector(selector).click()
    links = string(drive.find_element_by_tag_name('body')).split('\n')
    driver.quit()
    
    df = pd.DataFrame()
    
    for link in links:
        text = urllib.open(link).read()
        temp_df = parse_ascii(text)
        array = split_up(temp_df)
        array = np.random.choice(array, replace=False, size=(len(array) // FRACTION)) #select proportion of data
        to_add_df = to_df(array, temp_df.columns.values)
        
        df = pd.concat([df, to_add_df])
    
    df.to_csv(OUTPUT_FILE, index=False)

if __name__ == '__main__':
    main()
