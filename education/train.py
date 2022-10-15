import torch
from torch import nn
from torch.nn import functional as F
from torch.utils import data
import pandas as pd
import time

NUM_EPOCHS = 3 #nuber of epochs
BATCH_SIZE = 2000 #batch size
LEARNING_RATE = 0.01 #learning rate
PERCENTAGE = 90 #percentage of data that will be in the train split

get_fields = lambda line, fields: [line[field] for field in fields] #get given fields in a line

#split the dataframe by fields and into train/test
def field_split(df, inputs, outputs, percentage):
    inputs = [get_fields(line, inputs) for (_, line) in df.iterrows()] #get the input fields
    outputs = [get_fields(line, outputs) for (_, line) in df.iterrows()] #get the output fields
    partway = (len(df) * percentage) // 100 #get the integer value of a given percentage into the df
    train_inputs = inputs[:partway] #set the train inputs equal to the first percentage
    train_outputs = outputs[:partway] #set the train outputs equal to the second percentage
    test_inputs = inputs[partway:] #set the test inputs equal to the second percentage
    test_outputs = outputs[partway:] #set the test outputs equal to the second percentage
    return train_inputs, train_outputs, test_inputs, test_outputs

class SubDataset(data.Dataset):
    def __init__(self, sequences, targets, device):
        self.targets = torch.tensor(targets, device=device, dtype=torch.double) #set targets
        self.sequences = torch.tensor(sequences, device=device, dtype=torch.double) #set sequences

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
    #initialize layers
    def __init__(self, input_size, output_size):
        super(Model, self).__init__()
        self.fc1 = nn.Linear(input_size, 100)
        self.fc2 = nn.Linear(100, 100)
        self.fc3 = nn.Linear(100, 100)
        self.fc4 = nn.Linear(100, 100)
        self.fc5 = nn.Linear(100, 100)
        self.fc6 = nn.Linear(100, output_size)

    #forward pass
    def forward(self, inputs):
        x = F.relu(self.fc1(inputs))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = F.relu(self.fc5(x))
        x = torch.sigmoid(self.fc6(x))
        return x

def main():
    
    main_start = time.time()
    
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    
    df = pd.read_csv('augmented.csv') #read augmented data
    df = df.sample(frac=1) #shuffle data
    
    output_fields = ['Met and Above%'] #fields to be outputted
    input_fields = [column for column in df.columns.values if column not in output_fields] #fields to be inputted
    
    (train_inputs, train_outputs, 
    test_inputs, test_outputs) = field_split(df, input_fields, 
                                             output_fields, PERCENTAGE) #do field and train/test split
    
    schools = SubDataset(train_inputs, train_outputs, device) #make train dataset
    test_schools = SubDataset(test_inputs, test_outputs, device) #make test dataset
    input_size = len(schools.sequences[0]) #get input size
    output_size = len(schools.targets[0]) #get output size
    model = Model(input_size, output_size).double() #make a model with the input and output sizes
    criterion = nn.MSELoss() #loss criterion
    optimizer = torch.optim.SGD(model.parameters(), lr=LEARNING_RATE) #optimizer with given parameters and learning rate
    
    test_batch_size = BATCH_SIZE * len(test_schools) // len(schools) #get the batch size for test data
    
    for epoch in range(NUM_EPOCHS):
        print(f'\nEPOCH {epoch+1}\n') #print epoch number
        total_loss = 0 #keep track of loss
        start = time.time() #track time
        for i, (sequence, target) in enumerate(schools):
            output = model.forward(sequence) #forward pass
            loss = criterion(output, target) #get loss
            loss.backward() #backward pass
            optimizer.step() #optimizer step
            optimizer.zero_grad()
            total_loss += loss #add loss to total loss
            
            if (i+1) % BATCH_SIZE == 0:
            
                #the following code is to see how well the model is doing on the validation data
                step = (i+1) // BATCH_SIZE #which batch we are currently on
                beginning_value = test_batch_size * (step-1) #the first value of the test data to be used for this batch
                ending_value = test_batch_size * (step) #the last value of the test data to be used for this batch
                temp_seq = test_schools.sequences[beginning_value:ending_value] #whittle test sequences
                temp_targ = test_schools.targets[beginning_value:ending_value] #whittle test targets
                valid_loss = 0 #set the total validation loss equal to 0
                for ind, test_seq in enumerate(temp_seq):
                    test_targ = temp_targ[ind] #get the target corresponding to this sequence
                    output = model.forward(test_seq) #forward pass
                    loss = criterion(output, test_targ) #get loss
                    valid_loss += loss #add loss to total
                avg_valid_loss = valid_loss / len(temp_seq) #get average loss for this test batch
                
                avg_loss = total_loss / BATCH_SIZE #get average loss for train batch
                total_loss = 0 #reset total loss
                end = time.time() #get end time
                elapsed = end - start #get elapsed time
                print(f'Iteration number {i+1}.	Loss: {avg_loss:.3f}.	Time: {elapsed:.3f} seconds. Validation loss: {avg_valid_loss:.3f}') #report
                start = time.time() #reset start time
    
    main_end = time.time() #get final end time
    main_elapsed = main_end - main_start #get final elapsed time
    print(f'\n					Total elapsed: {main_elapsed:.1f} seconds.') #report
    
    torch.save(model, 'model\\model.pt') #save model to local directory

if __name__ == '__main__':
    main()