import pandas as pd
from collections import Counter
import multiprocessing
from multiprocessing import Pool

def get_wanted_list(first_df, second_df, second_axis, axis, wanted_axis, other_list, other_axis, i):
    final_other_list = []
    values = []
    i_list = []
    for other in other_list:
        final_other_list.append(other)
        temp_df = second_df[second_df[other_axis] == other]
        temp_df = temp_df[temp_df[second_axis] == axis]
        value_list = list(temp_df[wanted_axis])
        value = value_list[0] if len(value_list) > 0 else 0
        values.append(values)
        i_list.append(i)
    return values, final_other_list, i_list

def main():
    
    #consolidate basic information on latitude/longitude, status on charter/virtual/magnet/private,
    #demographics (gender/race), and percent of students that receive free or reduced price lunch
    
    #concatenate a column of a dataframe to another where a different axis has the same value
    def axis_concat(first_df, second_df, first_axis, second_axis, wanted_axis, other_axis, final_name):
        wanted_list = [] #make list of wanted values
        axis_list = list(first_df[first_axis]) #list of values in the first axis
        second_axes = list(second_df[second_axis].unique()) #list of unique values in second axis
        other_list = list(second_df[other_axis].unique()) #list of unique values in other axis
        value_list = [(first_df, second_df, second_axis, axis, wanted_axis, other_list, other_axis, i) for i, axis in enumerate(axis_list)]
        with Pool() as pool:
            all_values = pool.starmap(get_wanted_list, value_list)
        wanted_list = squish([item[0] for item in all_values])
        final_other_list = squish([item[1] for item in all_values])
        indeces = squish([item[2] for item in all_values])
        index_counter = Counter(indeces)
        for index in index_counter:
            appearances = index_counter[index] - 1
            line = pd.DataFrame(first_df.iloc[index]).transpose()
            for appearance in range(appearances):
                indeces = list(first_df.index.values)[:index] + [index] + list(first_df.index.values)[index:]
                first_df = pd.concat([first_df[:index], line, first_df[index:]])
                first_df.index = indeces
        first_df[final_name] = wanted_list
        first_df[other_axis] = final_other_list
        return first_df
    
    #concatenate two dataframes where to existing axes have the same value
    def existing_axis_concat(first_df, second_df, first_axis, second_axis, wanted_axis, other_axis, final_name):
        wanted_list = []
        for i in range(len(first_df)):
            line = first_df.iloc[i]
            temp_df = second_df[second_df[second_axis] == line[first_axis]]
            temp_df = temp_df[temp_df[other_axis] == line[other_axis]]
            value_list = list(temp_df[wanted_axis])
            value = value_list[0] if len(value_list) > 0 else 0
            wanted_list.append(value)
        first_df[wanted_axis] = wanted_list
        return first_df
    
    #consolidate information from various years from basic suffix
    def consolidate(basic, years, suffix, lowest):
        df = pd.DataFrame()
        for year in range(years):
            temp_df = pd.read_csv(f'{basic}{lowest+year}{suffix}.csv')
            length = len(temp_df.index)
            temp_df['Year'] = [f'20{lowest+year}' for _ in range(length)]
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
        if x == 'No Data':
            x = 'N'
        if x != 'N':
            x = 'Y'
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
    
    ids = list(df["CDSCode"])
    
    df = axis_concat(df, frpm_df, "CDSCode", "School Code", "Percent (%) \nEligible FRPM \n(Ages 5-17)", "Year", "Percent")
    
    genders = ['M', 'F']
    races = [i+1 for i in range(7)]
    race_genders = []
    for gender in genders:
        race_genders += [f'{gender}{race}' for race in races]
    for race_gender in race_genders:
        df = existing_axis_concat(df, demo_df, "CDSCode", "CDSCode", race_gender, "Year", race_gender)
    
    #write to csv
    df.to_csv('schools.csv', index=False)

if __name__ == '__main__':
    main()