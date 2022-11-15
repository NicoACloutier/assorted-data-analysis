import pandas as pd
import requests
import os
import re
from multiprocessing import Pool
import threading

BASIC = 'https://populationpyramid.net/api/pp'
DIRECTORY = '.\\countries'
YEARS = range(1950, 2019)
NUM_COUNTRIES = 1000
NUM_THREADS = 10
final_df = pd.DataFrame()

def url_to_file(url, directory, country, year):
    file = requests.get(url)
    if 'Server Error' in str(file.content):
        return None
    else:
        title = f'{directory}\\{country}-{year}.csv'
        with open(title, 'wb') as f:
            f.write(file.content)
        return title

#country names are messed up, TODO: FIX COUNTRY NAMES
#def get_info(filename):
#    info = filename.replace('.csv', '')
#    info = info.split('-')
#    country = info[0]
#    year = info[1]
#    return country, year
    
#change data to be on single row and percentages instead of absolute numbers
def normalize_df(filename, country, year):
    if filename:
        df = pd.read_csv(filename)
        country_dict = {'Year': year, 'Country': country}
        ages = list(df['Age']) #get list of age ranges
        total = sum(df['M']) + sum(df['F']) #get total population
        for gender in ['M', 'F']:
            df[gender] = df[gender].apply(lambda x: x*100/total) #rewrite as percentage
            for age in ages:
                #add the data for each age range to dict
                temp_df = df[df['Age'] == age]
                temp_df = temp_df[gender]
                item = temp_df.item()
                country_dict[f'{age}-{gender}'] = item
        
        output_df = pd.DataFrame([country_dict])
        return output_df
    else:
        return pd.DataFrame()
    
def country_iterate(range, lock):
    global final_df
    local_df = pd.DataFrame()
    for i in range:
        for year in YEARS:
            url = f'{BASIC}/{i}/{year}/?csv=true'
            filename = url_to_file(url, DIRECTORY, i, year)
            country_df = normalize_df(filename, i, year)
            local_df = pd.concat([local_df, country_df])
            if filename: os.remove(filename)
            else: break
    lock.acquire()
    final_df = pd.concat([local_df, final_df])
    lock.release()

def main():
    
    #TODO: speed up
    threads = []
    lock = threading.Lock()
    for x in range(NUM_THREADS):
        begin = NUM_COUNTRIES * x // NUM_THREADS
        end = NUM_COUNTRIES * (x+1) // NUM_THREADS
        thread = threading.Thread(target=country_iterate, args=(range(begin, end), lock))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    #with Pool() as pool:
    #    final_dfs = pool.starmap(country_iterate, inputs)
    
    #final_df = pd.concat(final_dfs)
    final_df.to_csv(f'{DIRECTORY}\\countries.csv', index=False)

if __name__ == '__main__':
    main()
