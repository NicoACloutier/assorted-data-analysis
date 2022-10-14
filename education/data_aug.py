import pandas as pd
import numpy as np
from numpy import random

def data_aug(collection):
    stdev = np.std(collection)
    stdev /= 10
    collection = [random.normal(0.0, stdev)+item for item in collection]
    return collection

def main():
    
    output_df = pd.DataFrame()
    df = pd.read_csv('for_model.csv')
    
    all_columns = df.columns.values
    output_columns = ['Met and Above%', 'Charter', 'Virtual', 'Magnet']
    binary_columns = ['Charter', 'Virtual', 'Magnet']
    input_columns = [item for item in all_columns if item not in output_columns]
    for_aug_columns = [item for item in input_columns if item not in binary_columns]
    
    times_augmented = 5
    
    for column in all_columns:
        final_column_values = list(df[column])
        column_values = list(df[column])
        if column in for_aug_columns:
            for _ in range(times_augmented-1):
                final_column_values += data_aug(column_values)
        else:
            for _ in range(times_augmented-1):
                final_column_values += column_values
        output_df[column] = final_column_values
    
    output_df.to_csv('augmented.csv', index=False)

if __name__ == '__main__':
    main()