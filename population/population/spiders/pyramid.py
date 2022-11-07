import scrapy
import pandas as pd
import requests
import os
import re

class PyramidSpider(scrapy.Spider):
    name = "populationpyramid"
    self.countries = [] #list to be filled with dfs for different countries
    year_list = range(1950, 2022, 5)

    def start_requests(self):
        urls = ['https://www.populationpyramid.net/']
        allowed_domains = ['www.populationpyramid.net']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    #get the individual data for a country for each year,
    #then add it to the countries list
    def parse(self, response):
    
        for year in year_list:
        
            #get country information
            country = response.css('.countryName dropbtn::text').get()
            filepath = f'..\\countries\\{country}.csv'
            
            #download csv file
            download_link = response.css('pp-csv-link a').get()
            file = requests.get(download_link)
            with open(filepath, 'w') as f:
                f.write(file)
            
            #change data to be on single row and percentages instead of absolute numbers
            df = pd.read_csv(filepath)
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
        
        #make df from country dict and save, delete csv
        output_df = pd.DataFrame(country_dict).transpose()
        os.remove(filepath)
        self.countries.append(output_df)
    
    #once data has been collected, compend them all to final df and write to csv
    def closed(self):
        final_final_df = pd.DataFrame()
        for df in self.countries:
            final_final_df = pd.concat([final_final_df, df])
        final_final_df.to_csv('..\\countries\\countries.csv')