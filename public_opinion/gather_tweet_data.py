import snscrape.modules.twitter as sntwitter
import pandas as pd

def transpose(matrix):
    num_rows = len(matrix[0])
    num_columns = len(matrix)
    Final = [[0]*num_columns for x in range(num_rows)]
    for x in range(num_rows):
        for i in range(num_columns):
            Final[x][i] = matrix[i][x]
    return Final

def add_zero(date):
    date = str(date)
    if len(date) == 1:
        date = '0' + date
    return date

companies = ["Tesla", "Microsoft", "Google"]

start_dates = [x+1 for x in range(11)]

limit = 1000
for company in companies:
    tweets = []
    for date_index, start_date in enumerate(start_dates):
        end_date = start_date + 1
        start_date = add_zero(start_date)
        end_date = add_zero(end_date)
        query = f"{company} lang:en until:2021-{end_date}-01 since:2021-{start_date}-01"
        for index, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            tweets.append([date_index+1, tweet.content])
            if index == limit-1:
                break
    tweets = transpose(tweets)
    tweet_df = pd.DataFrame(tweets, ['Month', 'Content'])
    tweet_df.to_csv(f'{company}.csv')