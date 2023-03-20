import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import urllib.request as request
import time
import numpy as np

URL = 'https://disc.gsfc.nasa.gov/datasets/M2I3NPASM_5.12.4/summary'
FRACTION = 100 #fraction of data to be kept, in form 1/FRACTION
DAYS_SURROUNDING = 4 #how many days surrounding the central day will be recorded on each side 
OUTPUT_FILE = '..\\data\\raw\\raw.csv'
CHROMEDRIVER_PATH = 'C:\\Users\\nicoc\\Documents\\chromedriver.exe'

#css selectors, name of variable is what button says
SUBSET_GET_DATA = ('.btn.btn-xs.btn-link.borderless.pop.ng-scope', 0)
DOWNLOAD_METHOD = ('.accordion-toggle', 0)
GET_FILE_SUBSETS_USING_OPENDAP = ('.ng-pristine.ng-untouched.ng-valid.ng-not-empty', 1)
VARIABLES = ('.accordion-toggle', 3)
FILE_FORMAT = ('.accordion-toggle', 4)
ASCII = ("//input[@class='ng-pristine ng-untouched ng-valid ng-not-empty']", 2)
GET_DATA = ('.btn.btn-success.modal-footer-btn', 0)
DOWNLOAD_LINK_LIST = ('.download-button', 0)

wait = lambda: time.sleep(3)

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
    for (selector, index) in button_list:
        element = driver.find_elements(By.CSS_SELECTOR, selector)[index]
        hover = ActionChains(driver).move_to_element(element)
        hover.perform()
        element.click()
        wait()

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
    for _ in range(40): wait() #have it wait for 1.5 minutes so the data can be generated
    
    url = driver.find_elements(By.CSS_SELECTOR, DOWNLOAD_LINK_LIST[0])[DOWNLOAD_LINK_LIST[1]].get_attribute('href')
    links = str(request.urlopen(url).read()).split('\\r\\n')[1:]
    driver.quit()
    
    df = pd.DataFrame()
    
    for link in links:
        text = request.urlopen(link).read()
        temp_df = parse_ascii(text)
        array = split_up(temp_df)
        array = np.random.choice(array, replace=False, size=(len(array) // FRACTION)) #select proportion of data
        to_add_df = to_df(array, temp_df.columns.values)
        
        df = pd.concat([df, to_add_df])
    
    df.to_csv(OUTPUT_FILE, index=False)

if __name__ == '__main__':
    main()
