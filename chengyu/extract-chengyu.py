import pandas as pd
import re

def main():
    
    filename = 'ankideck-raw.txt' #raw text file
    file = open(filename, 'r', encoding='utf8') #open file
    raw_text = file.read() #read file
    file.close() #close file
    chengyu_list = re.findall('(?<=<div id=""ent"">)....(?=</div> <div id=""from"">)', raw_text) #find all chengyu
    chengyu = pd.DataFrame([chengyu_list], ['Chengyu']) #create 1-column dataframe with all chengyu that appear in texts
    chengyu = chengyu.transpose() #transpose
    chengyu.to_csv('data\\all-chengyu.csv') #write to csv

if __name__ == '__main__':
    main()