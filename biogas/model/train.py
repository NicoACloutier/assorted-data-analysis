import sklearn
import xgboost
import pandas as pd
import numpy as np
from sklearn import svm, linear_model, preprocessing, tree, ensemble
import time

NUM_SPLITS = 10 #k for k-fold xvalidation

models = {'xgboost': xgboost.XGBRegressor,
          'linear': linear_model.LinearRegression,
          'svm': svm.SVR,
          'l1': linear_model.Lasso,
          'l2': linear_model.Ridge,
          'poly2': preprocessing.PolynomialFeatures,
          'poly3': preprocessing.PolynomialFeatures,
          'regtree': tree.DecisionTreeRegressor,
          'forest': ensemble.RandomForestRegressor,}

#split df into inputs and outputs
def split_df(df):
    input_columns = [column for column in df.columns.values if column not in ['Biogas', 'Essay', 'index']]
    
    input_list = [list(df[column]) for column in input_columns]
    inputs = np.array(input_list)
    outputs = np.array(list(df['Biogas']))
    return inputs, outputs
   
#get the answers for a model on test data and find differences
def test_models(model, inputs, outputs):
    answers = np.array(model.predict(inputs))
    return list(answers)

#train and test polynomial features
def train_test_polynomial(poly, inputs, outputs, test_inputs, test_outputs):
    inputs = poly.fit_transform(inputs)
    test_inputs = poly.fit_transform(test_inputs)
    model = linear_model.LinearRegression()
    model.fit(inputs, outputs)
    answers = np.array(model.predict(test_inputs))
    return list(answers)

#train and test models
def train_models(train_df, test_df):
    all_differences = []
    inputs, outputs = split_df(train_df)
    inputs, outputs = inputs.T, outputs.T
    
    test_inputs, test_outputs = split_df(test_df)
    test_inputs, test_outputs = test_inputs.T, test_outputs.T

    for model_name in models:
        start = time.time()
        
        if 'poly' in model_name:
            degree = int(model_name[-1]) #find the degree of the polynomial
            poly = models[model_name](degree=degree) #initialize model
            differences = train_test_polynomial(poly, inputs, outputs, test_inputs, test_outputs)
        else:
            model = models[model_name]() #initialize model
            model.fit(inputs, outputs)
            differences = test_models(model, test_inputs, test_outputs)
        
        all_differences.append(differences)
        end = time.time()
        print(f'Finished training {model_name} in {end-start:.2f} seconds.')
    
    return all_differences

def main():
    all_answers = []

    df = pd.read_csv('..\\data\\for_model\\biogas.csv')
    df = df.sample(frac=1)
    df = df.dropna()
    jump = len(df) // NUM_SPLITS
    left_over = df.iloc[jump*NUM_SPLITS:]
    df = df.drop(left_over.index) #get rid of left over samples
    
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
            if i < len(all_answers):
                all_answers[i] += column
            else:
                all_answers.append(column)
    
    data_dict = dict()
    data_dict['Actual'] = df['Biogas']
    for (i, column) in enumerate(models.keys()):
        data_dict[column] = all_answers[i]
    
    output_df = pd.DataFrame(data_dict)
    output_df.to_csv('..\\data\\for_model\\answers.csv', index=False)

if __name__ == '__main__':
    main()
