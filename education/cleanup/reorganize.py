def main():
    import pandas as pd
    import re
    
    #REORGANIZE TEST DATA
    
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
    ' es': '',
    ' ms': '',
    ' hs': '',
    ' ec': '',
    ' bs': '',
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
        if school_name == float('NaN'):
            school_name = 'empty'
        school_name = school_name.lower()
        for key in replace_dict:
            school_name = school_name.replace(key, replace_dict[key]) #normalize school names
        if '@' in school_name: #get rid of @
            ind = school_name.index('@')
            school_name = school_name[:ind-1]
        if ' at ' in school_name: #get rid of at
            ind = school_name.index(' at ')
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
            df_columns = ["Name", "Year"] + columns
            averages = pd.DataFrame(columns = df_columns) #dataframe with column names and school names
            even_more_temp_df = temp_df[temp_df['Year'] == year] #whittle df
            for i, column in enumerate(columns):
                values = even_more_temp_df[column] #get values for that year and that column
                average = sum(values) / len(values) #get average values
                averages[column] = [average]
            averages["Name"] = name
            averages["Year"] = year
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

    averages = averages.sort_values(['Name', 'Year'])
    averages.to_csv('test.csv', index=False)
    
    #REORGANIZE BUDGET DATA
    
    #open up a budget csv file
    def open_budget(budget, budget_dict, year):
        (name_id, budget_id) = budget_dict[budget] #get information on column names for school name and budget allocation
        df = pd.read_csv(f'raw\\{budget}.csv', low_memory=False) #read budget csv
        return_df = pd.DataFrame(columns=['Name', 'Budget', 'Year']) #df to be returned
        df = df[[name_id, budget_id]]
        df = df.dropna()
        return_df['Name'] = pd.Series([normalize(name, replace_dict) for name in df[name_id]], dtype='string') #get and normalize school name
        return_df['Budget'] = pd.Series(df[budget_id], dtype='float32') #get budget id
        return_df['Year'] = pd.Series([year for _ in range(len(df[name_id]))], dtype='category') #add year column
        return return_df
    
    #combine the budget within a single school and year
    def combine_budget(budget_df):
        return_df = pd.DataFrame(columns=['Name', 'Budget', 'Year'])
        schools = list(budget_df['Name'].unique()) #list of unique schools
        for school in schools:
            school_list = []
            temp_df = budget_df[budget_df['Name'] == school]
            years = list(temp_df['Year'].unique())
            for year in years:
                even_more_temp_df = temp_df[temp_df['Year'] == year]
                overall = sum(list(even_more_temp_df['Budget']))
                school_list.append({'Name': school, 'Budget': overall, 'Year': year})
            school_df = pd.DataFrame(school_list)
            return_df = pd.concat([return_df, school_df])
        return return_df
    
    budget_dict = {
    'b14': ('School', 'Amount'),
    'b15': ('school_name', 'total_cost'),
    'b16': ('school_name', 'amount'),
    'b17': ('School Name', 'Total School Budget Allocation'),
    }
    
    budgets = [f'b1{4+i}' for i in range(4)] #budget files
    
    #make dataframes of budgets
    budget_df = pd.DataFrame(columns=['Name', 'Budget', 'Year'])
    for i, budget in enumerate(budgets):
        year = f'201{4+i}'
        temp_df = open_budget(budget, budget_dict, year) #open budget file
        budget_df = pd.concat([temp_df, budget_df]) #add to budget df
    
    budget_df = combine_budget(budget_df) #combine the budget for each year and each school
    budget_df = budget_df.sort_values(['Name', 'Year'])
    budget_df.to_csv('budget.csv', index=False)

if __name__ == '__main__':
    main()