def main():
    import pandas as pd
    import re
    
    filename = 'ankideck-raw.txt'
    file = open(filename, 'r', encoding='utf8')
    raw_text = file.read()
    chengyu_list = re.findall('(?<=<div id=""ent"">)....(?=</div> <div id=""from"">)', raw_text)
    chengyu = pd.DataFrame([chengyu_list], ['Chengyu'])
    chengyu = chengyu.transpose()
    chengyu.to_csv('all-chengyu.csv')

if __name__ == '__main__':
    main()