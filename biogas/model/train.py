import sklearn
import xgboost
import pandas as pd
import numpy as np
from sklearn import svm, linear_model, preprocessing
import time

NUM_SPLITS = 10 #k for k-fold xvalidation

models = {'xgboost': xgboost.XGBClassifier,
          'svm': svm.SVC,
          'linear': linear_model.LinearRegression,
          'l1': linear_model.Lasso,
          'l2': linear_model.Ridge,
          'poly2': preprocessing.PolynomialFeatures,
          'poly3': preprocessing.PolynomialFeatures,}

#split df into inputs and outputs
def split_df(df):
    input_columns = [column for column in df.columns.values if column not in ['Biogas', 'Esssay']]
    
    inputs = np.array([list(df[column]) for column in input_columns])
    outputs = np.array(list(df['Biogas']))
    return inputs, outputs
   
#get the answers for a model on test data and find differences
def test_models(model, inputs, outputs):
    answers = np.array(model.predict(inputs))
    differences = [np.dot(outputs[i]-answers[i], outputs[i]-answers[i]) for (i, _) in enumerate(answers)] #get how far off the model was
    return differences

#train and test models
def train_models(train_df, test_df):
    all_differences = []
    inputs, outputs = split_df(train_df)
    test_inputs, test_outputs = split_df(test_df)

    for model_name in models:
        start = time.time()
        if 'poly' in model_name:
            degree = int(model_name[-1]) #find the degree of the polynomial
            model = models[model_name](degree=degree) #initialize model
        else:
            model = models[model_name]() #initialize model
        model.fit(inputs, outputs)
        differences = test_models(model, test_inputs, test_outputs)
        all_differences.append(differences)
        end = time.time()
        printf(f'Finished training {model_name} in {end-start:.2f} seconds.')
    
    return all_differences

def main():
    all_answers = []

    df = pd.read_csv('..\\data\\for_model\\biogas.csv')
    jump = len(df) // NUM_SPLITS
    
    for split in range(NUM_SPLITS):
        test_begin = split * jump
        test_end = (split+1) * jump
    
        #split to train and test for this partition
        test_df = df.iloc[test_begin:test_end]
        train_df = df.drop(test_df.index)
        test_df = test_df.reset_index()
        train_df = train_df.reset_index()
        
        #train models, get answers for test data, and write to file
        answers = train_models(train_df, test_df)
        for (i, column) in enumerate(answers):
            all_answers[i] += column
    
    output_df = pd.DataFrame(data=all_answers, columns=models.keys())
    output_df.to_csv('..\\data\\for_model\\answers.csv', index=False)

if __name__ == '__main__':
    main()
