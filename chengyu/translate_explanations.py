import deepl
import os
import pandas as pd

def main():
    
    auth_key = os.environ['DEEPL-KEY'] #get api key
    translator = deepl.Translator(auth_key) #make translator
    df = pd.read_csv('data\\Chengyu-Final.csv') #read data
    chengyu_list = df['Chengyu'].to_list() #get chengyu
    explain_list = df['Explanation'].to_list() #get explanations
    
    translated_list = []
    for explanation in explain_list:
        result = translator.translate_text(explanation, target_lang='EN-US') #translate
        translated_list.append(result.text) #add text to list
    
    output_df = pd.DataFrame([chengyu_list, translated_list], ["Chengyu", "Explanation"]) #make dataframe with chengyu and explanations
    output_df = output_df.transpose() #transpose
    output_df.to_csv('data\\en-explanations.csv') #write to csv

if __name__ == '__main__':
    main()