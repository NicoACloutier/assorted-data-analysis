import torch
from torch import nn
from torch.nn import functional as F
from torch.utils import data

get_fields = lambda line, fields: [line[field] for field in fields] #get given fields in a line

#split the dataframe by fields and into train/test
def field_split(df, inputs, outputs, percentage):
    inputs = [get_fields(line, inputs) for _, line in df.iterrows()] #get the input fields
    outputs = [get_fields(line, outputs) for _, line in df.iterrows()] #get the output fields
    partway = (len(df) * percentage) // 100 #get the integer value of a given percentage into the df
    train_inputs = inputs[:partway] #set the train inputs equal to the first percentage
    train_outputs = outputs[:partway] #set the train outputs equal to the second percentage
    test_inputs = inputs[partway:] #set the test inputs equal to the second percentage
    test_outputs = outputs[partway:] #set the test outputs equal to the second percentage
    return train_inputs, train_outputs, test_inputs, test_outputs

class SubDataset(data.Dataset):
    def __init__(self, sequences, targets, test_sequences, test_targets, device):
        self.targets = torch.tensor(targets, device=device, dtype=torch.double) #set targets
        self.sequences = torch.tensor(sequences, device=device, dtype=torch.double) #set sequences
        self.test_seq = torch.tensor(test_sequences, device=device, dtype=torch.double) #set test sequences
        self.test_tar = torch.tensor(test_targets, device=device, dtype=torch.double) #set test targets

    def __getitem__(self, i): return (self.sequences[i], self.targets[i])
    def __len__(self): return len(self.sequences)
        
    def __iter__(self):
        self.i = -1
        return self
        
    def __next__(self):
        self.i += 1
        if self.i < len(self):
            return self[self.i]
        raise StopIteration

class Model(nn.Module):
    def __init__(self, input_size, output_size):
        super(Model, self).__init__()
        self.fc1 = nn.Linear(input_size, 100)
        self.fc2 = nn.Linear(100, 100)
        self.fc3 = nn.Linear(100, output_size)

    def forward(self, inputs):
        x = F.relu(self.fc1(inputs))
        x = F.relu(self.fc2(x))
        x = F.sigmoid(self.fc3(x))
        return x

def main():
    import pandas as pd
    import time
    
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    
    df = pd.read_csv('for_model.csv')
    df = df.sample(frac=1)
    
    percentage = 90
    output_fields = ['Met and Above%']
    input_fields = [column for column in df.columns.values if column not in output_fields]
    
    (train_inputs, train_outputs, 
    test_inputs, test_outputs) = field_split(df, input_fields, 
                                             output_fields, percentage)
    
    schools = SubDataset(train_inputs, train_outputs, test_inputs, test_outputs, device)
    input_size = len(schools.sequences[0])
    output_size = len(schools.targets[0])
    model = Model(input_size, output_size).double()
    num_epochs = 3
    batch_size = 500
    learning_rate = 0.01
    criterion = nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    
    start = time.time()
    
    for epoch in range(num_epochs):
        for i, (sequence, target) in enumerate(schools):
            output = model.forward(sequence)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            
            if (i+1) % batch_size == 0:
                end = time.time()
                elapsed = end - start
                print(f'Iteration number {i+1}. Loss: {loss:.3f}. Time: {elapsed:.3f} seconds.')
                start = time.time()
        

if __name__ == '__main__':
    main()