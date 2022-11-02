import scrapy
import pandas as pd

class PyramidSpider(scrapy.Spider):
    name = "pyramid"
    self.countries = [] #list to be filled with DFs for different countries

    def start_requests(self):
        urls = ['https://www.populationpyramid.net/',]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        final_df = pd.DataFrame()
        for year in years:
            country = self.whatever #get back to this part
            country_dict = {'Year': year, 'Country': country}
            df = pd.DataFrame(self.whatever) #get back to this part
            ages = list(df['Age'])
            total = sum(df['M']) + sum(df['F'])
            for gender in ['M', 'F']:
                df[gender].apply(lambda x: x*100/total)
                for age in ages:
                    temp_df = df[df['Age'] == age]
                    temp_df = temp_df[gender]
                    item = temp_df.item()
                    country_dict[f'{age}-{gender}'] = item
            output_df = pd.DataFrame(country_dict).transpose()
            final_df = pd.concat([final_df, output_df])
        self.countries.append(final_df)
    
    def closed(self):
        final_final_df = pd.DataFrame()
        for df in self.countries:
            final_final_df = pd.concat([final_final_df, df])
        final_final_df.to_csv('..\\countries\\countries.csv')