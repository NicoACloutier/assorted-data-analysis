def main():
    import pandas as pd
    from collections import Counter
    import re
    
    def overlap_counter(string, length):
        final_counter = dict()
        final_counters = []
        all_groups = []
        string = [char for char in string]
        divided_length = int(len(string)/length)
        indeces = [index*length for index in range(divided_length)]
        for i in range(length):
            temp_list = []
            temp_indeces = [index+i for index in indeces]
            for x, index in enumerate(temp_indeces):
                if index != temp_indeces[-1]:
                    next_index = temp_indeces[x+1]
                    temp_group = ''.join(string[index:next_index])
                    temp_list.append(temp_group)
                    all_groups.append(temp_group)
            temp_counter = Counter(temp_list)
            final_counters.append(temp_counter)
        all_groups = list(set(all_groups))
        for group in all_groups:
            total = 0
            for counter in final_counters:
                total += counter[group]
            final_counter[group] = total
        return final_counter
    
    text_df = pd.read_csv('train.csv', encoding='utf8')
    texts = text_df['content'].to_list()
    texts = ' '.join(texts)
    four_char_counter = overlap_counter(texts, 4)
    
    chengyu = pd.read_csv('all-chengyu.csv')
    chengyu = chengyu['Chengyu'].to_list()
    
    appears = []
    appearances = []
    for cy in chengyu:
        if cy in four_char_counter:
            appears.append(cy)
            appearances.append(four_char_counter[cy])
    final_chengyu = pd.DataFrame([appears, appearances], ['Chengyu', 'Appearances'])
    final_chengyu = final_chengyu.transpose()
    final_chengyu.to_csv('chengyu-appearances.csv')

if __name__ == '__main__':
    main()