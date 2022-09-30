def main():
    import pandas as pd
    
    #whittle down a df to rows where a particular column has a particular value
    whittle = lambda df, column, value: df[df[column] == value]
    
    #columns in df that have to have a certain value
    necessary_values = {
    'StatusType': 'Active', #make sure all schools are active
    'EILName': 'High School' #make sure all schools are high schools
    }
    
    #read csv
    df = pd.read_csv('raw\\pubschls.csv')
    
    #whittle df
    for value in necessary_values:
        df = whittle(df, value, necessary_values[value])
    
    #get list of unwanted columns
    columns = list(df.columns.values)
    keep_columns = [
    'CDSCode', 'County', 'District', 'School', 'City',
    'SOCType', 'Virtual', 'Magnet', 'Latitude', 'Longitude',
    'Charter', 'Virtual'
    ]
    bad_columns = [column for column in columns if column not in keep_columns]
    
    #delete unwanted columns
    for column in bad_columns:
        del df[column]
    
    #write to csv
    df.to_csv('publicschools.csv', index=False)

if __name__ == '__main__':
    main()