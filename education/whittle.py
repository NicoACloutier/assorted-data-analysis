import pandas as pd
import multiprocessing
from multiprocessing import Pool

#The purpose of this file is to get consolidate information about schools into one document, schools.csv.
#The file takes in basic information from the list of schools like physical location, county/district, 
#school name, identification numbers, and whether or not it's a charter, magnet, or virtual school,
#and combines it with data regarding demographics (including gender and race makeup of the school),
#test scores (including percentage of students meeting the standard or higher, as well as other measures),
#and free and reduced priced meals (just a simple proportion of how many students receive them).

#get a value in a dataframe in a row where two other row-column values are equal to the same values
#in another dataframe
def get_single_wanted(first_df, second_df, first_axis, second_axis, wanted_axis, other_axis, i):
    line = first_df.iloc[i] #get line in the first dataframe with index i
    temp_df = second_df[second_df[second_axis] == line[first_axis]] #whittle second dataframe to only values equal to line values on first axis
    temp_df = temp_df[temp_df[other_axis] == line[other_axis]] #whittle second dataframe to only values equal to line values on second axis
    value_list = list(temp_df[wanted_axis]) #get list of values
    value = value_list[0] if len(value_list) > 0 else None #set value equal to first value if there are any, and otherwise to missing
    value = None if value == "*" else value #set values of "*" equal to None because it is used to represent missing values
    return value

def main():
    
    #expand a dataframe to add a new column, duplicating each existing row to have each individual
    #value in the column
    def expand_df(df, expand_values, column_name):
        final_df = pd.DataFrame() #initialize output dataframe
        df_length = len(df) #get length of input dataframe
        values_length = len(expand_values) #get length of values given
        wanted_axis = [] #new row to be added
        for column in df.columns.values:
            column_list = list(df[column]) #get a list of values in a column
            column_list = squish([column_list for _ in range(values_length)]) #duplicate the list for the number of values given, add to one big list
            final_df[column] = column_list #change column in final dataframe to this new list
        for value in expand_values: wanted_axis += [value] * df_length #make big list of values for each value given
        final_df[column_name] = wanted_axis #add to final dataframe
        return final_df
    
    #concatenate two dataframes where two existing axes have the same value
    #(for example, if you have two dataframes with axis 1 and axis 2, and the other one has an axis three,
    # and you want to add an axis 3 to the first one, you can add a column to the first dataframe where
    #axis 3 values will only appear in rows where axis 1 and 2 are the same as the same axes in the second
    #dataframe)
    # first_df = dataframe you want to add the value to
    # second_df = dataframe that has the value you want to add
    # first_axis and second_axis = the names of the first columns that you want to align with each other
    # wanted_axis = the name of the column in the second dataframe you want to add to the first
    # other_axis = the other axis you want to align them by (have to have the same name in both dataframes)
    # final_name = the name of the final column added to the first dataframe
    def axis_concat(first_df, second_df, first_axis, second_axis, wanted_axis, other_axis, final_name):
        input_values = [(first_df, second_df, first_axis, 
                         second_axis, wanted_axis, other_axis, i) for i in range(len(first_df))] #get list of input values as tuples
        with Pool() as pool:
            wanted_list = pool.starmap(get_single_wanted, input_values) #perform get_single_wanted function on each tuple
        first_df[final_name] = wanted_list #add column to df
        return first_df
    
    #consolidate information from csv files that have the same names with different
    #years at the end, given a lowest year, the number of years you want to include,
    #the basic format of the files, and a suffix after the year (same for all files),
    #plus a list of years you want to disclude
    def consolidate(basic, years, suffix, lowest, disclude):
        df = pd.DataFrame()
        for year in range(years):
            if lowest+year not in disclude:
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
    
    #clean up a dataframe, getting only rows with the necessary values, only the columns you want to keep,
    #renaming badly names columns, delete unwanted columns after having done this, create columns with uniform
    #values, and make columns that should be binary binary.
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
    
    #replace strings with substring that are keys in a dictionary
    #with the values of that dictionary
    def sub(str, replace_dict):
        for to_be_replaced in replace_dict:
            replacement = replace_dict[to_be_replaced]
            str = str.replace(to_be_replaced, replacement)
        return str
    
    #race correspondences
    repl = {"1": "-American Indian",
            "2": "-Asian",
            "3": "-Pacific Islander",
            "4": "-Filipino",
            "5": "-Hispanic",
            "6": "-African American",
            "7": "-White"}
    
    #make the schools dataframe
    df = make_df('raw\\pubschls.csv', {'StatusType': 'Active',
                                       'EILName': 'High School'}, 
                ['CDSCode', 'County', 'District', 
                 'School', 'City', 'Virtual', 'Charter',
                 'Magnet', 'Latitude', 'Longitude'], dict(), ['Virtual', 'Magnet', 'Charter'], [], [])
    
    frpm_df = consolidate('raw\\frpm\\frpm', 6, '-cut', 16, []) #consolidate free and reduced priced lunch data
    test_df = consolidate('raw\\test\\test', 6, '-cut', 16, [20]) #consolidate test data
    demo_df = pd.read_csv('raw\\demographics.csv') #get demographic data
    
    df = expand_df(df, [2016, 2017, 2018, 2019, 2020, 2021], 'Year') #expand school dataframe to include years
    
    df = axis_concat(df, frpm_df, "CDSCode", "School Code", "Percent (%) \nEligible FRPM \n(Ages 5-17)", "Year", "FRPM%") #concatenate frpm data
    
    levels = ["Exceeded", "Met", "Met and Above", "Nearly Met", "Not Met"]
    for level in levels:
        df = axis_concat(df, test_df, "CDSCode", "School Code", f"Percentage Standard {level}", "Year", f"{level}%") #concatenate test data
    
    genders = ['M', 'F']
    races = [i+1 for i in range(7)]
    race_genders = []
    for gender in genders:
        race_genders += [f'{gender}{race}' for race in races]
    for rg in race_genders:
        df = axis_concat(df, demo_df, "CDSCode", "CDSCode", rg, "Year", sub(rg,repl)) #concatenate gender/race data
    
    df.to_csv('schools.csv', index=False) #write to csv

if __name__ == '__main__':
    main()