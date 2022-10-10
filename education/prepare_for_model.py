#The purpose of this file is to prepare the data consolidated in schools.csv for being used as the training/test data for a model.
#It will write the final data to for_model.csv.

def main():
    import pandas as pd
    
    #convert column with "Y"/"N" values to column with 1/0 values
    def yn_to_10(df, column):
        repl_dict = {'Y': 1, 'N': 0}
        values = list(df[column])
        values = [repl_dict[value] for value in values]
        df[column] = values
        return df
    
    #fill a column with the mean of that column
    def fill_mean(df, column):
        values = df[column]
        values = values.fillna(values.mean())
        df[column] = values
        return df
    
    #subtract the mean of a column from every value in that column
    def subtract_mean(df, column):
        mean = df[column].mean()
        df[column] = df[column].apply(lambda x: x - mean)
        return df
    
    #get total percentage for a race or gender
    #(currently, the columns laid out in the format {gender}-{race} where the column
    #has the percentage of people that are both of that gender and that race. This will organize
    #it into seperate columns for each race and gender).
    def get_totals(df, race_gender, name):
        totals = []
        columns = [column for column in df.columns.values if (f'{race_gender}-' in column) or (f'-{race_gender}' in column)]
        for _, row in df.iterrows(): 
            total = 0
            for column in columns:
                value = row[column]
                total += value
            totals.append(total)
        df[name] = totals
        return df
    
    df = pd.read_csv('schools.csv') #read csv
    
    #remove unwanted columns
    unwanted_columns = ['CDSCode', 'County', 'District', 'School', 'City',
                        'Met%', 'Nearly Met%', 'Not Met%', 'Exceeded%']
    for column in unwanted_columns:
        del df[column]
    
    #convert columns in 'Y'/'N' format to 1/0 format
    binary_list = ['Charter', 'Virtual', 'Magnet']
    for column in binary_list:
        df = yn_to_10(df, column)
    
    #get rid of rows for 2020 (when no testing occured), then delete year column
    df = df[df['Year'] != 2020]
    del df['Year']
    
    #fill missing values in all columns except the one with testing data with the mean for the column
    columns = [value for value in df.columns.values if value != 'Met and Above%']
    for column in columns:
        df = fill_mean(df, column)
    
    df = df.dropna() #get rid of missing values
    
    #subtract the mean latitude and longitude from each value in these columns.
    #this is because the current latitude/longitude are significantly larger than the other
    #values in the table, this is to get them to the same ballpark.
    too_big = ['Latitude', 'Longitude']
    for too_big_column in too_big:
        df = subtract_mean(df, too_big_column)
    
    df['Met and Above%'] = df['Met and Above%'].apply(lambda x: x / 100) #change 'Met and Above%' values from percentages to proportions
    
    df = get_totals(df, 'M', 'Male%') #get percentage of males in each school
    
    #get percentage of each race in each school
    race_genders = []
    genders = ['M', 'F']
    races = ['American Indian', 'Asian', 'Pacific Islander', 
             'Filipino', 'Hispanic', 'African American', 'White']
    for race in races:
        for gender in genders: race_genders.append(f'{gender}-{race}')
        if race != 'White': df = get_totals(df, race, f'{race}%') #don't do it for white because you only need n-1 columns for proportions
    
    #delete old race/gender columns, only keep new ones
    for race_gender in race_genders:
        del df[race_gender]
    
    df.to_csv('for_model.csv', index=False) #write to csv

if __name__ == '__main__':
    main()