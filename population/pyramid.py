import pandas as pd
import requests
import os
import threading

#This script downloads population pyramid data from the website https://populationpyramid.net. It collects each file for
#each country/region in each year and transforms each of them into a single row containing population percentage for each population
#group (split into gender and age), with that row also containing information on which country the data are from and which
#year they represent.

BASIC = 'https://populationpyramid.net/api/pp'
DIRECTORY = '.\\countries'
YEARS = range(1950, 2019)
NUM_COUNTRIES = 1000
NUM_THREADS = 10
final_df = pd.DataFrame()

#get country name from id and df with ids and names
def get_name(id, df):
    df = df[df['LocID'] == id]['Location']
    if len(df) != 0:
        return df.item() 
    else:
        return id

#get_name = lambda id, df: df[df['LocID'] == id]['Location'].item() #get country name from id and df with ids and names

def url_to_file(url, directory, country, year):
    file = requests.get(url)
    
    #return None if there is no file
    if 'Server Error' in str(file.content):
        return None
    
    #otherwise, write to file and return filename
    else:
        title = f'{directory}\\{country}-{year}.csv'
        with open(title, 'wb') as f:
            f.write(file.content)
        return title
    
#change data to be on single row and percentages instead of absolute numbers
def normalize_df(filename, country, year, code_df):
    if filename:
        df = pd.read_csv(filename)
        country_dict = {'Year': year, 'Country': get_name(country, code_df)}
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
    
#iterate through a list of country ids, turn them to dataframes,
#concatenate to one big dataframe, and in the end concat that to the global
#final df
def country_iterate(range, lock, code_df):
    global final_df
    local_df = pd.DataFrame()
    for i in range:
        for year in YEARS:
            url = f'{BASIC}/{i}/{year}/?csv=true'
            filename = url_to_file(url, DIRECTORY, i, year) #write to local file and get filename
            country_df = normalize_df(filename, i, year, code_df) #normalize the country/year df
            local_df = pd.concat([local_df, country_df])
            
            #if no file was found on the website, break iteration for this country id
            if filename: os.remove(filename)
            else: break
    lock.acquire()
    final_df = pd.concat([local_df, final_df])
    lock.release()

def main():
    
    code_df = pd.read_csv(f'{DIRECTORY}\\codes.csv') #dataframe with location ids stored in column 'LocID' and location names stored in column 'Location'
    
    threads = []
    lock = threading.Lock()
    for x in range(NUM_THREADS):
        begin = NUM_COUNTRIES * x // NUM_THREADS #the beginning country id for this thread
        end = NUM_COUNTRIES * (x+1) // NUM_THREADS #the ending country id for this thread
        thread = threading.Thread(target=country_iterate, args=(range(begin, end), lock, code_df))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    final_df.to_csv(f'{DIRECTORY}\\countries.csv', index=False)

if __name__ == '__main__':
    main()
