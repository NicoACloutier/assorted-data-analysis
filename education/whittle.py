def main():
    import pandas as pd
    
    #set a column in a df with all the same value
    def set_values(df, column, value):
        length = len(df)
        values = [value for _ in range(length)]
        df[column] = values
        return df
    
    #whittle down a df to rows where a particular column has a particular value
    whittle = lambda df, column, value: df[df[column] == value]
    
    def make_df(file, necessary, keep_columns, uniform_values, to_binary):
        def binary_func(x):
            if x == 'No Data':
                x = 'N'
            if x != 'N':
                x = 'Y'
            return x
        #read csv
        df = pd.read_csv(file)
        #whittle df
        for value in necessary:
            df = whittle(df, value, necessary[value])
        #get list of unwanted columns
        columns = list(df.columns.values)
        bad_columns = [column for column in columns if column not in keep_columns]
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
                         'Magnet', 'Latitude', 'Longitude'], {'Public Yes/No': 'Y'}, ['Virtual', 'Magnet', 'Charter'])
    
    private_df = make_df('raw\\prvschls.csv', {'Entity Type': 'High Schools (Private)'}, 
                        ['Public Yes/No', 'County', 'District', 'School', 'CDSCode', 'Latitude', 'Longitude'],
                        {'Charter': 'N', 'Virtual': 'N', 'Magnet': 'N'}, [])
    
    df = pd.concat([public_df, private_df])
    
    #write to csv
    df.to_csv('publicschools.csv', index=False)

if __name__ == '__main__':
    main()