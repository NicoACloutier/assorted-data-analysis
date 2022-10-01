def main():
    import pandas as pd
    
    school_df = pd.read_csv('schools.csv')
    school_ids = list(school_df['CDSCode'])
    
    genders = ['M', 'F']
    races = [i+1 for i in range(7)]
    
    basic = 'raw\\demographics\\filesenr'
    num_files = 6
    lowest = 16
    
    df = pd.DataFrame()
    
    for i in range(num_files):
        file = f'{basic}{lowest+i}.csv'
        temp_df = pd.read_csv(file)
        for school_id in school_ids:
            school_dict = {'CDSCode': school_id, 'Year': lowest+i}
            temp_df = temp_df[temp_df['CDS_CODE'] == school_id]
            all_sum = sum([int(item) for item in temp_df['ENR_TOTAL']])
            for race in races:
                if race in list(temp_df['ETHNIC'].unique()):
                    even_more_temp_df = temp_df[temp_df['ETHNIC'] == race]
                    for gender in genders:
                        if gender in list(even_more_temp_df['GENDER'].unique()):
                            value = int(list(even_more_temp_df[even_more_temp_df['GENDER'] == gender])[0])
                            percent = value / all_sum
                            school_dict[f'{gender}{race}'] = percent
            temp_series = pd.Series(school_dict)
            df = pd.concat([df, temp_series])
    
    df.to_csv('raw\\demographics.csv')

if __name__ == '__main__':
    main()