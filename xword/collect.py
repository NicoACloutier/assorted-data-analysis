import pandas as pd
from requests
import re
import json
import threading

#Collect the xword data, turn to readable format

REPO_URL = 'https://raw.githubusercontent.com/doshea/nyt_crosswords/master'
NUM_THREADS = 10
all_dict = dict()

add_zero = lambda x: f'0{x}' if len(str(x)) == 1 else str(x)
remove = lambda x: re.sub('^[0-9]+?\. ', '', x) #remove the initial numbers

#join two dictionaries
def join(dict1, dict2):
    for key in dict2:
        dict1[key] = dict2[key]
    return dict1

#parse an xword json in a particular direction
def parse(json_dict, direction):
    answer_dict = dict()
    answers = json_dict['answers'][direction]
    clues = json_dict['clues'][direction]
    clues = [remove(clue) for clue in clues]
    for (i, clue) in enumerate(clues):
        answer_dict[clue] = answers[i]
    return answer_dict

#collect answer and clue data from urls
def collect(urls, lock):
    global all_dict
    local_all_dict = dict()
    
    for url in urls:
        try:
            raw = requests.get(url).content
            json_dict = json.loads(raw)
            answer_dict = join(parse(json_dict, 'across'), parse(json_dict, 'down'))
            local_all_dict = join(answer_dict, local_all_dict)
            driver.quit()
        except Exception:
            pass
    
    lock.acquire()
    all_dict = join(local_all_dict, all_dict)
    lock.release()
    

def main():
    lock= threading.Lock()
    all_dict = dict()
    
    urls = []
    for year in range(1976, 2018):
        for month in range(1, 13):
            for day in range(1, 32):
                urls.append(f'{REPO_URL}/{year}/{add_zero(month)}/{add_zero(day)}.json')
    
    num_urls = len(urls)
    threads = []
    for x in range(NUM_THREADS):
        begin = num_urls * x // NUM_THREADS #the beginning url index for this thread
        end = num_urls * (x+1) // NUM_THREADS #the endind url index for this thread
        thread = threading.Thread(target=collect, args=(range(begin, end), lock))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    df = pd.DataFrame()
    df['Clue'] = all_dict.keys()
    df['Answer'] = all_dict.values()
    
    df.to_csv('.\\data\\xword.csv', index=False)

if __name__ == '__main__':
    main()
