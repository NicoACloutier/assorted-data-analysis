import torch
import pandas as pd 
import train
from train import Model
import numpy as np

#split the dataframe by fields
def field_split(df, inputs, outputs):
    inputs = [train.get_fields(line, inputs) for (_, line) in df.iterrows()] #get the input fields
    outputs = [train.get_fields(line, outputs) for (_, line) in df.iterrows()] #get the output fields
    return inputs, outputs

def main():
    
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    df = pd.read_csv('test.csv')
    df = df.sample(frac=1)
    output_fields = ['Met and Above%'] #fields to be outputted
    input_fields = [column for column in df.columns.values if column not in output_fields] #fields to be inputted
    inputs, outputs = field_split(df, input_fields, output_fields)
    test_schools = train.SubDataset(inputs, outputs, device)
    
    differences = []
    with torch.no_grad():
        model = Model(13, 1).double()
        model = torch.load('model\\model.pt')
        model.eval()
        for sequence, target in test_schools:
            output = model.forward(sequence).item()
            target = target.item()
            difference = target - output
            differences.append(difference)
    
    avg_difference = sum([abs(difference) for difference in differences]) / len(differences)
    
    print(f'Average absolute value of difference: {avg_difference}.')

if __name__ == '__main__':
    main()