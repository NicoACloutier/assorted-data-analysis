import pandas as pd
import numpy as np
from numpy import random

#add noise to a collection
def data_aug(collection):
    stdev = np.std(collection) #get the standard deviation of a collection
    stdev /= 10 #divide standard deviation by 10
    collection = [random.normal(0.0, stdev)+item for item in collection] #add random numbers from a normal distribution with the reduced standard deviation
    return collection

def main():
    
    output_df = pd.DataFrame() #initialize output dataframe
    df = pd.read_csv('for_model.csv') #read information for model
    
    all_columns = df.columns.values #get column names
    output_columns = ['Met and Above%'] #columns used for output (not to be changed)
    binary_columns = ['Charter', 'Virtual', 'Magnet'] #columns with binary values (not to be changed)
    input_columns = [item for item in all_columns if item not in output_columns] #input columns
    for_aug_columns = [item for item in input_columns if item not in binary_columns] #columns that are to be changed (not output and not binary)
    
    times_augmented = 5 #how many times over the dataframe will be increased in size
    
    for column in all_columns:
        final_column_values = list(df[column]) #initialize final column values with values in the column (this will be changed)
        column_values = list(df[column]) #get the original values (this will not be changed)
        #if the column should be changed, change it. Otherwise, just add it again
        if column in for_aug_columns:
            for _ in range(times_augmented-1):
                final_column_values += data_aug(column_values) #add the column with some noise
        else:
            for _ in range(times_augmented-1):
                final_column_values += column_values #add the column with no noise
        output_df[column] = final_column_values #set that column of the output df
    
    output_df.to_csv('augmented.csv', index=False) #write to csv

if __name__ == '__main__':
    main()