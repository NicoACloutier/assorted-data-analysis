import pandas as pd
import sklearn
from sklearn import linear_model, neighbors, tree
import pickle
import math
import tensorflow as tf
import sys
import os

BASIC = '.\\countries'
MODEL_DIR = '.\\models'
INDICATORS = ['gdp', 'military_percent', 'bribery', 'top_share']
NUM_EPOCHS = 10
BATCH_SIZE = 300

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
def test_model(model, test_input, test_output, outputs, is_nn):
    output_dict = dict()
    if is_nn:
        predictions = model.predict(test_input, verbose=0)
    else:
        predictions = model.predict(test_input)
    
    for (i, output) in enumerate(outputs):
        temp_predictions = [item[i] for item in predictions]
        temp_output = [item[i] for item in test_output]
        output_sum = sum(temp_output)
        distance = vector_distance(temp_predictions, temp_output) * 100 / output_sum
        output_dict[output] = distance
    return output_dict
    
#fit a model, save to file, and test
def fit_save_test(model, model_name, train_input, train_output, 
                  test_input, test_output, num_epochs=NUM_EPOCHS, batch_size=BATCH_SIZE):
    
    if model_name == 'neural_network':
        model.fit(train_input, train_output, epochs=num_epochs, batch_size=batch_size, verbose=0)
    else:
        model.fit(train_input, train_output)
    
    filename = f'{MODEL_DIR}\\{model_name}.sav'
    pickle.dump(model, open(filename, 'wb'))
    distance = test_model(model, test_input, test_output, INDICATORS, model_name == 'neural_network')
    return distance
    
def main():

    old_stdout = sys.stdout # backup current stdout

    #load test and train datasets, put into proper format
    train_df = pd.read_csv(f'{BASIC}\\aggregated_train.csv')
    test_df = pd.read_csv(f'{BASIC}\\aggregated_test.csv')
    input_columns = [column for column in train_df.columns.values if column not in INDICATORS]
    
    (train_input, train_output) = io_split(train_df, input_columns, INDICATORS)
    (test_input, test_output) = io_split(test_df, input_columns, INDICATORS)
    
    tf_model = tf.keras.models.Sequential()
    Dense = tf.keras.layers.Dense
    backend = tf.keras.backend
    
    tf_model.add(Dense(units=100, activation='tanh', input_dim=len(train_input[0])))
    for _ in range(5): tf_model.add(Dense(units=1000, activation='tanh'))
    tf_model.add(Dense(units=len(train_output[0]), activation='sigmoid'))
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.1)
    tf_model.compile(loss='mse', optimizer=optimizer, metrics='accuracy')
    
    models = {'linear': linear_model.LinearRegression(),
              'k-nearest': neighbors.KNeighborsRegressor(),
              'decision-tree': tree.DecisionTreeRegressor(),
              'neural_network': tf_model}
    
    print()
    for model in models:
        sys.stdout = open(os.devnull, "w")
        distance_dict = fit_save_test(models[model], model, train_input, 
                                      train_output, test_input, test_output)
        sys.stdout = old_stdout
        print(f'{model.title()} model fitted.')
        for variable in INDICATORS:
            print(f'{variable} distance: {distance_dict[variable]:.3f}')
        print()

if __name__ == '__main__':
    main()
