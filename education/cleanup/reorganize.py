def main():
    import pandas as pd
    import re
    
    replace_dict = {
    'elementary school': 'es',
    'middle school': 'ms',
    'high school': 'hs',
    'education campus': 'ec',
    'bilingual school': 'bs',
    'm l ': '',
    '-': ' ',
    'high': 'h',
    '.': ' ',
    '  ': ' ',
    }
    
    #get only the average scores across grades and delete unnecessary columns
    def get_tests(filename):
        filename = f'raw\\{filename}.csv'
        df = pd.read_csv(filename) #open csv
        if 'All' in df['Grade']: df = df[df['Grade'] == 'All'] #only keep average rows for schools
        elif 'ALL' in df['Grade']: df = df[df['Grade'] == 'ALL']
        del df['Grade'] #delete grade row (all values should now be 'All')
        del df['School Code ']
        columns = list(df.columns.values) #get list of columns
        bad_columns = [column for column in columns if ('#' in column) or (column.startswith('NCSC')) or (column.endswith('Proficient')) or column.startswith('MSAA')] #get list of unwanted columns
        for column in bad_columns: del df[column] #delete unwanted columns
        return df
    
    #normalize the school names
    def normalize(school_name, replace_dict):
        school_name = school_name.lower()
        for key in replace_dict:
            school_name = school_name.replace(key, replace_dict[key]) #normalize school names
        if '@' in school_name: #get rid of @
            ind = school_name.index('@')
            school_name = school_name[:ind-1]
        school_name = re.sub(' ?\(.+?\)', '', school_name) #get rid of parentheses
        return school_name
    
    #get the average score for each school
    def school_average(name, df, replace_dict):
        temp_df = df[df['School Name '] == name] #get only columns for that school
        del temp_df['School Name '] #delete school name column
        name = normalize(name, replace_dict) #normalize name
        years = temp_df['Year'].unique() #get unique years
        columns = list(temp_df.columns.values) #list of columns
        columns.remove('Year') #remove year from columns
        return_df = pd.DataFrame() #df to be returned
        for year in years:
            averages = pd.DataFrame(columns = ["Name", "Column", "Average", "Year"]) #dataframe with column names and school names
            even_more_temp_df = temp_df[temp_df['Year'] == year] #whittle df
            for i, column in enumerate(columns):
                values = even_more_temp_df[column] #get values for that year and that column
                average = sum(values) / len(values) #get average values
                averages.loc[i] = pd.Series({"Name": name, "Column": column, "Average": average, "Year": year})
            return_df = pd.concat([return_df, averages])
        return return_df
    
    tests = [f't1{4+i}' for i in range(4)] #test score files
    
    test_df = pd.DataFrame()
    for i, test in enumerate(tests):
        temp_df = get_tests(test) #get test df
        rows = len(temp_df.index) #find number of rows
        years = [f'201{4+i}' for _ in range(rows)] #make list of years same length as rows
        temp_df['Year'] = years #make year column
        test_df = pd.concat([test_df, temp_df]) #add to test df
    
    
    schools = list(set(test_df['School Name ']))
    
    averages = pd.DataFrame()
    for school in schools:
        school_df = school_average(school, test_df, replace_dict)
        averages = pd.concat([school_df, averages])

    averages.to_csv('raw\\test.csv', index=False)

if __name__ == '__main__':
    main()