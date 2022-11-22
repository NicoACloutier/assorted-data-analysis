import pandas as pd
import sklearn
from sklearn import linear_model, neighbors, tree
import pickle
import math
import tensorflow as tf

BASIC = '.\\countries'
MODEL_DIR = '.\\models'
INDICATORS = ['gdp', 'military_percent', 'bribery', 'top_share']

vector_distance = lambda v1, v2: math.sqrt(sum([(v1[i]-v2[i])**2 for (i, _) in enumerate(v1)])) #distance between two vectors equation

#copy only certain columns from one dataframe to another
def whittle_df(df, columns):
    output_df = pd.DataFrame()
    for column in columns:
        output_df[column] = df[column]
    return output_df

#split dataframe by input and output columns
def io_split(df, input_columns, output_columns):
    inputs = whittle_df(df, input_columns).values.tolist()
    outputs = whittle_df(df, output_columns).values.tolist()
    return (inputs, outputs)
    
#get vector distance between predictions and output on test dataset
def test_model(model, test_input, test_output, outputs):
    output_dict = dict()
    predictions = model.predict(test_input)
    for (i, output) in enumerate(outputs):
        temp_predictions = [item[i] for item in predictions]
        temp_output = [item[i] for item in test_output]
        output_sum = sum(temp_output)
        distance = vector_distance(temp_predictions, temp_output) * 100 / output_sum
        output_dict[output] = distance
    return output_dict
    
#fit a model, save to file, and test
def fit_save_test(model, model_name, train_input, train_output, test_input, test_output):
    model.fit(train_input, train_output)
    filename = f'{MODEL_DIR}\\{model_name}.sav'
    pickle.dump(model, open(filename, 'wb'))
    distance = test_model(model, test_input, test_output, INDICATORS)
    return distance
    
def main():

    #load test and train datasets, put into proper format
    train_df = pd.read_csv(f'{BASIC}\\aggregated_train.csv')
    test_df = pd.read_csv(f'{BASIC}\\aggregated_test.csv')
    input_columns = [column for column in train_df.columns.values if column not in INDICATORS]
    
    (train_input, train_output) = io_split(train_df, input_columns, INDICATORS)
    (test_input, test_output) = io_split(test_df, input_columns, INDICATORS)
    
    non_nn_models = {'linear': linear_model.LinearRegression(),
                     'k-nearest': neighbors.KNeighborsRegressor(),
                     'decision-tree': tree.DecisionTreeRegressor()}
    
    for model in non_nn_models:
        distance_dict = fit_save_test(non_nn_models[model], model,
                                 train_input, train_output, test_input, test_output)
        print(f'\n{model.title()} model fitted.')
        for variable in INDICATORS:
            print(f'{variable} distance: {distance_dict[variable]:.3f}')
    

if __name__ == '__main__':
    main()
