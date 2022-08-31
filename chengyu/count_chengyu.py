def main():
    import pandas as pd
    from collections import Counter
    import re
    
    #create a Counter that counts all substrings of a certain length in a string (includes overlap)
    def overlap_counter(string, length):
        final_counter = dict() #the counter that will be returned
        final_counters = [] #list of counters that will be added together
        all_groups = [] #list of all substrings of a certain length
        string = [char for char in string] #convert to list
        divided_length = int(len(string)/length) #the length of the string divided by the length
        indeces = [index*length for index in range(divided_length)] #increment by the length
        for i in range(length):
            temp_list = [] #list of all substrings in a certain increment setting
            temp_indeces = [index+i for index in indeces] #offset increment by i
            for x, index in enumerate(temp_indeces):
                if index != temp_indeces[-1]: #check the index if not the final one
                    next_index = temp_indeces[x+1] #fetch next index
                    temp_group = ''.join(string[index:next_index]) #join character elements of list into substring
                    temp_list.append(temp_group) #append group to temporary group
                    all_groups.append(temp_group) #append group to list of all groups
            temp_counter = Counter(temp_list) #create a counter of the temporary list for this specific offset
            final_counters.append(temp_counter) #append to list of counters
        all_groups = list(set(all_groups)) #delete repeats in the list of all groups
        for group in all_groups:
            total = 0 #initialize total number of occurences
            for counter in final_counters:
                total += counter[group] #iterate through list of counters on each offset and add occurences on that offset
            final_counter[group] = total #create entry in final counter with total occurences
        return final_counter
    
    text_df = pd.read_csv('train.csv', encoding='utf8') #read sentence list
    texts = text_df['content'].to_list() #get column 'content' (the actual sentence list)
    texts = ' '.join(texts) #put all into one string
    four_char_counter = overlap_counter(texts, 4) #execute overlap_counter() on texts with substring length 4
    
    chengyu = pd.read_csv('all-chengyu.csv') #get list of all chengyu
    chengyu = chengyu['Chengyu'].to_list() #get 'Chengyu' (actual list of chengyu)
    
    appears = []
    appearances = []
    for cy in chengyu:
        if cy in four_char_counter: #check if the chengyu is in the text
            appears.append(cy) #append it to a list of appearing chengyu
            appearances.append(four_char_counter[cy]) #append its number of appearances to the list of frequency amounts
    final_chengyu = pd.DataFrame([appears, appearances], ['Chengyu', 'Appearances']) #create a dataframe with chengyu and appearances
    final_chengyu = final_chengyu.transpose() #transpose dataframe
    final_chengyu.to_csv('chengyu-appearances.csv') #write to csv

if __name__ == '__main__':
    main()