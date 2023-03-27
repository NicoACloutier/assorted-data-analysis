import sklearn
import xgboost
import sqlite3
import pandas as pd
import numpy as np
import time

NUM_SPLITS = 10 #k for k-fold xvalidation
NUM_SURROUNDING = 4

models = {'xgboost': xgboost.XGBClassifier,}

#split df into inputs and outputs
def split_df(df):
    input_columns = []
    for x in range(NUM_SURROUNDING+1):
        input_columns += [column for column in df.columns.values if f'{x+1}' in column]
    
    output_columns = [column for column in df.columns.values if column not in input_columns]
    inputs = np.array([list(df[column]) for column in input_columns])
    outputs = np.array([list(df[column]) for column in output_columns])
    return inputs, outputs
   
#get the answers for a model on test data and find differences
def test_models(model, inputs, outputs):
    answers = np.array(model.predict(inputs))
    differences = [np.sqrt((outputs[i] - answers[i])**2) for (i, _) in enumerate(answers)] #get how far off the model was
    return differences

#train and test models
def train_models(train_df, test_df):
    all_differences = []
    inputs, outputs = split_df(train_df)
    test_inputs, test_outputs = split_df(test_df)

    for model_name in models:
        start = time.time()
        model = models[model_name]() #initialize model
        model.fit(inputs, outputs)
        differences = test_models(model, test_inputs, test_outputs)
        all_differences.append(differences)
        end = time.time()
        printf(f'Finished training {model_name} in {end-start:.3f} seconds.')
    
    return all_differences

def main():
    all_answers = []

    connection = sqlite3.connect('..\\database\\weather.db')
    df = pd.read_sql_query("SELECT * FROM weather", connection)
    jump = len(df) // NUM_SPLITS
    
    for split in range(NUM_SPLITS):
        test_begin = split * jump
        test_end = (split+1) * jump
    
        test_df = df.iloc[test_begin:test_end]
        train_df = df.drop(test_df.index)
        test_df = test_df.reset_index()
        train_df = train_df.reset_index()
        
        answers = train_models(train_df, test_df)
        for (i, column) in enumerate(answers):
            all_answers[i] += column
    
    output_df = pd.DataFrame(data=all_answers, columns=models.values())
    output_df.to_csv('..\\data\\for_model\\answers.csv', index=False)

if __name__ == '__main__':
    main()