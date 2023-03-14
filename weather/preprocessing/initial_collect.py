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
SUBSET_GET_DATA = ('btn.btn-xs.btn-link.borderless.pop.ng-scope', 0)
DOWNLOAD_METHOD = ('accordion-toggle', 0)
GET_FILE_SUBSETS_USING_OPENDAP = ('ng-valid.ng-not-empty.ng-dirty.ng-valid-parse.ng-touched', 1)
VARIABLES = ('accordion-toggle', 3)
FILE_FORMAT = ('accordion-toggle', 0)
ASCII = ('ng-valid.ng-not-empty.ng-dirty.ng-valid-parse.ng-touched', 0)
GET_DATA = ('btn.btn-success.modal-footer-btn', 0)
DOWNLOAD_LINK_LIST = ('download-button.download-link-disabled', 0)

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

#click on each of the buttons in a list
def click_buttons(driver, button_list):
    for (selector, index) in button_selectors:
        driver.find_elements_by_css_selector(selector)[index].click()
        
        #close dropdown if the item is a dropdown
        if selector == 'accordion-toggle':
            driver.find_elements_by_css_selector(selector)[index].click()
    

def main():
    driver.get(URL)
    button_selectors = [SUBSET_GET_DATA, DOWNLOAD_METHOD, GET_FILE_SUBSETS_USING_OPENDAP] #initial buttons
    
    click_buttons(driver, button_selectors) #click the initial buttons
    
    #click on all of the variables
    driver.find_elements_by_css_selector(VARIABLES[0])[VARIABLES[1]].click()
    for element in driver.find_elements_by_css_selector('checkbox-inline'):
        element.click()
    driver.find_elements_by_css_selector(VARIABLES[0])[VARIABLES[1]].click()
    
    click_buttons(driver, [FILE_FORMAT, ASCII, GET_DATA]) #click on the final buttons
    
    links = string(drive.find_element_by_tag_name('body')).split('\n')[1:] #first link is readme, ignore
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
