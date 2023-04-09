import sklearn
import xgboost
import pandas as pd
import numpy as np
from sklearn import svm, linear_model, preprocessing, tree, ensemble, cluster
import imblearn
import pickle

NUM_SPLITS = 10 #k for k-fold xvalidation

models = {'xgboost': xgboost.XGBRegressor,
          'linear': linear_model.LinearRegression,
          'l1': linear_model.Lasso,
          'l2': linear_model.Ridge,
          'poly2': preprocessing.PolynomialFeatures,
          'poly3': preprocessing.PolynomialFeatures,
          'regtree': tree.DecisionTreeRegressor,
          'forest': ensemble.RandomForestRegressor,}

methods = {'RandomOver': imblearn.over_sampling.RandomOverSampler,
           'RandomUnder': imblearn.under_sampling.RandomUnderSampler,
           'none': None,}

#split df into inputs and outputs
def split_df(df):
    input_columns = [column for column in df.columns.values if column not in ['Biogas', 'Essay', 'index']]
    
    input_list = [list(df[column]) for column in input_columns]
    inputs = np.array(input_list)
    outputs = np.array(list(df['Biogas']))
    return inputs.T, outputs.T
   
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
def train_models(train_df, test_df, kmean_labels, method):
    all_differences = []
    inputs, outputs = split_df(train_df)
    
    if method != 'none':
        (inputs, _) = methods[method](random_state=0).fit_resample(inputs, kmean_labels.reshape(-1, 1))
        outputs = methods[method](random_state=0).fit_resample(outputs.reshape(-1, 1), kmean_labels.reshape(-1, 1))[0].ravel()
    
    test_inputs, test_outputs = split_df(test_df)

    for model_name in models:
        if 'poly' in model_name:
            degree = int(model_name[-1]) #find the degree of the polynomial
            poly = models[model_name](degree=degree) #initialize model
            differences = train_test_polynomial(poly, inputs, outputs, test_inputs, test_outputs)
        else:
            model = models[model_name]() #initialize model
            model.fit(inputs, outputs)
            differences = test_models(model, test_inputs, test_outputs)
        
        all_differences.append(differences)
    
    return all_differences

#train final model on all of the data
def train_final(model_name, df):
    inputs, outputs = split_df(df)
    if 'poly' in model_name:
        degree = int(model_name[-1]) #find the degree of the polynomial
        poly = models[model_name](degree=degree) #initialize model
        inputs = poly.fit_transform(inputs)
        model = linear_model.LinearRegression()
    else:
        model = models[model_name]()
    
    model.fit(inputs, outputs)
    with open(f'saves\\{model_name}.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    if 'poly' in model_name:
        with open(f'saves\\poly-{model_name}.pkl', 'wb') as f:
            pickle.dump(poly, f)

def test_method(df, kmean_labels, method):
    all_answers = []

    jump = len(df) // NUM_SPLITS
    for split in range(NUM_SPLITS):
        test_begin = split * jump
        test_end = (split+1) * jump
    
        #split to train and test for this partition
        test_df = df.iloc[test_begin:test_end]
        train_df = df.drop(test_df.index)
        test_df = test_df.reset_index()
        train_df = train_df.reset_index()
        
        temp_kmean_labels = np.array([label for (i, label) in enumerate(kmean_labels) if not test_begin <= i < test_end])
        
        #train models, get answers for test data, and write to file
        answers = train_models(train_df, test_df, temp_kmean_labels, method)
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
    output_df.to_csv(f'..\\data\\for_model\\answers-{method}.csv', index=False)

def main():
    df = pd.read_csv('..\\data\\for_model\\biogas.csv')
    df = df.drop('Essay', axis=1)
    df = df.sample(frac=1)
    df = df.dropna()
    jump = len(df) // NUM_SPLITS
    left_over = df.iloc[jump*NUM_SPLITS:]
    df = df.drop(left_over.index) #get rid of left over samples
    kmean_labels = list(cluster.KMeans(n_clusters=3).fit(df.drop('Biogas', axis=1)).labels_)
    
    for method in methods:
        test_method(df, kmean_labels, method)
    
    for model in models:
        train_final(model, df)

if __name__ == '__main__':
    main()
