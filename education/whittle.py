import pandas as pd
from collections import Counter
import multiprocessing
from multiprocessing import Pool

def get_single_wanted(first_df, second_df, first_axis, second_axis, wanted_axis, other_axis, i):
    line = first_df.iloc[i]
    temp_df = second_df[second_df[second_axis] == line[first_axis]]
    temp_df = temp_df[temp_df[other_axis] == line[other_axis]]
    value_list = list(temp_df[wanted_axis])
    value = value_list[0] if len(value_list) > 0 else None
    return value

def main():
    
    #consolidate basic information on latitude/longitude, status on charter/virtual/magnet/private,
    #demographics (gender/race), and percent of students that receive free or reduced price lunch
    
    def expand_df(df, expand_values, column_name):
        final_df = pd.DataFrame()
        df_length = len(df)
        values_length = len(expand_values)
        wanted_axis = []
        for column in df.columns.values:
            column_list = list(df[column])
            column_list = squish([column_list for _ in range(values_length)])
            final_df[column] = column_list
        for value in expand_values: wanted_axis += [value] * df_length
        final_df[column_name] = wanted_axis
        return final_df
    
    #concatenate two dataframes where two existing axes have the same value
    def axis_concat(first_df, second_df, first_axis, second_axis, wanted_axis, other_axis, final_name):
        input_values = [(first_df, second_df, first_axis, 
                         second_axis, wanted_axis, other_axis, i) for i in range(len(first_df))]
        with Pool() as pool:
            wanted_list = pool.starmap(get_single_wanted, input_values)
        first_df[final_name] = wanted_list
        return first_df
    
    #consolidate information from various years from basic suffix
    def consolidate(basic, years, suffix, lowest):
        df = pd.DataFrame()
        for year in range(years):
            temp_df = pd.read_csv(f'{basic}{lowest+year}{suffix}.csv')
            length = len(temp_df.index)
            temp_df['Year'] = [int(f'20{lowest+year}') for _ in range(length)]
            df = pd.concat([df, temp_df])
        return df
    
    #get a vector from a matrix
    def squish(collection):
        final = []
        for row in collection:
            final += row
        return final
    
    #set a column in a df with all the same value
    def set_values(df, column, value):
        length = len(df)
        values = [value for _ in range(length)]
        df[column] = values
        return df

    #function to make any data either Y or N
    def binary_func(x):
        if x == 'No Data' or x == None: x = 'N'
        if x != 'N': x = 'Y'
        return x
    
    #whittle down a df to rows where a particular column has a particular value
    whittle = lambda df, column, value: df[df[column] == value]
    
    def make_df(file, necessary, keep_columns, uniform_values, to_binary, rename_list, to_rename_list):
        #read csv
        df = pd.read_csv(file)
        #whittle df
        for value in necessary:
            df = whittle(df, value, necessary[value])
        #get list of unwanted columns
        columns = list(df.columns.values)
        bad_columns = [column for column in columns if column not in keep_columns]
        #rename columns to be renames
        for i, rename in enumerate(rename_list):
            to_rename = to_rename_list[i]
            to_add_list = list(df[rename])
            df[to_rename] = to_add_list
            del df[rename]
        #delete unwanted columns
        for column in bad_columns:
            del df[column]
        #create uniform series values
        for value in uniform_values:
            df = set_values(df, value, uniform_values[value])
        #change values in column to Y if not N
        for column in to_binary:
            df[column] = df[column].apply(binary_func)
        return df
    
    def sub(str, replace_dict):
        for to_be_replaced in replace_dict:
            replacement = replace_dict[to_be_replaced]
            str = str.replace(to_be_replaced, replacement)
        return str
    
    repl = {"1": "-American Indian",
            "2": "-Asian",
            "3": "-Pacific Islander",
            "4": "-Filipino",
            "5": "-Hispanic",
            "6": "-African American",
            "7": "-White"}
    
    public_df = make_df('raw\\pubschls.csv', {'StatusType': 'Active',
                                              'EILName': 'High School'}, 
                        ['CDSCode', 'County', 'District', 
                         'School', 'City', 'Virtual', 'Charter',
                         'Magnet', 'Latitude', 'Longitude'], {'Public Yes/No': 'Y'}, ['Virtual', 'Magnet', 'Charter'], [], [])
    
    private_df = make_df('raw\\prvschls.csv', {'Entity Type': 'High Schools (Private)'}, 
                        ['Public Yes/No', 'County', 'District', 'School', 'CDS Code', 'Latitude', 'Longitude'],
                        {'Charter': 'N', 'Virtual': 'N', 'Magnet': 'N'}, [], ["CDS Code"], ["CDSCode"])
    
    df = pd.concat([public_df, private_df])
    
    frpm_df = consolidate('raw\\frpm\\frpm', 6, '-cut', 16)
    demo_df = pd.read_csv('raw\\demographics.csv')
    
    df = expand_df(df, [2016, 2017, 2018, 2019, 2020, 2021], 'Year')
    
    df = axis_concat(df, frpm_df, "CDSCode", "School Code", "Percent (%) \nEligible FRPM \n(Ages 5-17)", "Year", "FRPM%")
    
    genders = ['M', 'F']
    races = [i+1 for i in range(7)]
    race_genders = []
    for gender in genders:
        race_genders += [f'{gender}{race}' for race in races]
    for rg in race_genders:
        df = axis_concat(df, demo_df, "CDSCode", "CDSCode", rg, "Year", sub(rg,repl))
    
    #write to csv
    df.to_csv('schools.csv', index=False)

if __name__ == '__main__':
    main()