from typer import Typer
import pandas as pd

#make a frequency rating out of stars and spaces with an integer 1 to 5
def make_freq(number):
    output = number * '*' #start with a number of asterisks the same as the input value
    difference = 5 - number #get difference between 5 and number
    output += ' ' * difference #add difference number of spaces to stars
    return output

#read data
df = pd.read_csv('Chengyu-Final.csv')
del df['Unnamed: 0']
key_list = df['Chengyu'].to_list()

#cli setup
app = Typer()

#command to check if a single chengyu is in the list
@app.command()
def chengyu(key):
    if key in key_list: #check if it's in the list
        i = key_list.index(key) #get the row index
        o = df.iloc[i] # find row
        #print info
        print(f"{o['Chengyu']}: {o['Pinyin']}\n\nDefinition: {o['Definition']}\nTranslation: {o['English Definition']}\n\n{o['Topic']}, {make_freq(int(o['Frequency']))}\n\n{o['Example']}")
    else:
        print(f'{key} not found.')
    
#command to find the chengyu in a sentence and get their information
@app.command()
def sentence(input):
    for value in key_list: #iterate through each value
        if value in input: #check if it's in the input
            chengyu(value) #print the info
            print('\n')


if __name__ == '__main__':
    app()