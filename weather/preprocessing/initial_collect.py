import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import requests
import time
import numpy as np
import os
import sqlite3

#This script downloads the data from 1980 to the latest date from the MDISC site. There is a lot of data, so it only saves a subset.

URL = 'https://disc.gsfc.nasa.gov/datasets/M2I3NPASM_5.12.4/summary'
PROPORTION = 0.001 #fraction of data to be kept, in form 1/FRACTION
DAYS_SURROUNDING = 4 #how many days surrounding the central day will be recorded on each side 
OUTPUT_FILE = '..\\data\\raw\\raw.csv'
CHROMEDRIVER_PATH = 'C:\\Users\\nicoc\\Documents\\chromedriver.exe'
DATABASE_PATH = '..\\data\\database\\weather.db'

#for this script to work, you have to have environment variables with the following names saved with user and password
USERNAME = os.environ['MDISC_DATA_USER']
PASSWORD = os.environ['MDISC_DATA_PASSWORD']

#css selectors, name of variable is what button says
SUBSET_GET_DATA = ('.btn.btn-xs.btn-link.borderless.pop.ng-scope', 0)
DOWNLOAD_METHOD = ('.accordion-toggle', 0)
GET_FILE_SUBSETS_USING_OPENDAP = ('.ng-pristine.ng-untouched.ng-valid.ng-not-empty', 1)
VARIABLES = ('.accordion-toggle', 3)
FILE_FORMAT = ('.accordion-toggle', 4)
ASCII = ("//input[@class='ng-pristine ng-untouched ng-valid ng-not-empty']", 2)
GET_DATA = ('.btn.btn-success.modal-footer-btn', 0)
DOWNLOAD_LINK_LIST = ('.download-button', 0)

wait = lambda: time.sleep(5)

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
    array = np.resize(array, (array.shape[0], (DAYS_SURROUNDING * 2) + 1, array.shape[1]))
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
    for (selector, index) in button_list:
        element = driver.find_elements(By.CSS_SELECTOR, selector)[index]
        hover = ActionChains(driver).move_to_element(element)
        hover.perform()
        element.click()
        wait()

#read the text from a list of ascii links
def read_ascii_links(links):
    df = pd.DataFrame()
    
    for link in links:
        #actually read the ascii, process
        text = str(requests.get(link, auth=(USERNAME, PASSWORD)).content)
        temp_df = parse_ascii(text)
        array = split_up(temp_df)
        np.random.shuffle(array)
        end = int(len(array) * PROPORTION) + 1
        array = array[:end]
        to_add_df = to_df(array, temp_df.columns.values)
        
        #write to df
        df = pd.concat([df, to_add_df])
    
    return df

def main():
    driver = webdriver.Chrome(CHROMEDRIVER_PATH)
    driver.get(URL)
    wait()
    button_selectors = [SUBSET_GET_DATA, DOWNLOAD_METHOD, GET_FILE_SUBSETS_USING_OPENDAP, DOWNLOAD_METHOD, VARIABLES] #initial buttons
    
    click_buttons(driver, button_selectors) #click the initial buttons
    
    #click all variable names
    wait()
    for element in driver.find_elements(By.CSS_SELECTOR, '.checkbox-inline'):
        element.click()
    wait()
    
    click_buttons(driver, [VARIABLES, FILE_FORMAT])
    
    #ascii button just really wants to be different
    element = driver.find_elements(By.XPATH, ASCII[0])[ASCII[1]]
    hover = ActionChains(driver).move_to_element(element)
    hover.perform()
    element.click()
    
    click_buttons(driver, [FILE_FORMAT, GET_DATA]) #click on the final buttons
    for _ in range(30): wait() #have it wait for some time so the data can be generated
    
    url = driver.find_elements(By.CSS_SELECTOR, DOWNLOAD_LINK_LIST[0])[DOWNLOAD_LINK_LIST[1]].get_attribute('href')
    links = str(requests.get(url).content).split('\\r\\n')[1:]
    driver.quit()
    
    df = read_ascii_links(links)
    
    connection = sqlite3.connect(DATABASE_PATH)
    df.to_sql(con=connection, name='raw_weather', if_exists='replace', flavor='sqlite')
    
    df = df.sample(frac=0.01) #save subset of data to local file, just to view structure
    df.to_csv(OUTPUT_FILE, index=False)

if __name__ == '__main__':
    main()
