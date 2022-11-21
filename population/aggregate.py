import pandas as pd
import random

BASIC = '.\\countries'

def main():
    indicators = ['gdp', 'military_percent', 'bribery', 'top_share'] #variables to be predicted by model
    
    df = pd.read_csv(f'{BASIC}\\population.csv')
    for indicator in indicators:
        indicator_df = pd.read_csv(f'{BASIC}\\{indicator}.csv')
        values = list(indicator_df['Value'])
        avg_value = sum(values)/len(values)
        indicator_list = []
        for (_, row) in df.iterrows():
            country = row['Country']
            year = row['Year']
            country_indicator_df = indicator_df[indicator_df['Country'] == country]
            temp_indicator_df = country_indicator_df[country_indicator_df['Year'] == year]
            
            #set the value to be added equal to the value of that country for that year.
            #if there is no such value, select a random value from that country in some year.
            #if that country has no data for any year, set the value equal to the average value
            #for the whole world.
            if len(temp_indicator_df) == 1:
                value = temp_indicator_df['Value'].item()
            else:
                if len(country_indicator_df) >= 1:
                    temp_values = list(country_indicator_df['Value'])
                    value = random.choice(temp_values)
                else:
                    value = avg_value
            
            indicator_list.append(value)
        df[indicator] = indicator_list
    
    df.to_csv(f'{BASIC}\\aggregated.csv', index=False)

if __name__ == '__main__':
    main()
