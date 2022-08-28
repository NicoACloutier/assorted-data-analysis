import snscrape.modules.twitter as sntwitter
import pandas as pd

#transpose a matrix
def transpose(matrix):
    num_rows = len(matrix[0])
    num_columns = len(matrix)
    Final = [[0]*num_columns for x in range(num_rows)]
    for x in range(num_rows):
        for i in range(num_columns):
            Final[x][i] = matrix[i][x]
    return Final

#change an int to a string. if it's only made up of one character,
#add a zero to the beginning. (this is because of the way twitter 
#handles dates)
def add_zero(date):
    date = str(date)
    if len(date) == 1:
        date = '0' + date
    return date

companies = ["Tesla", "Microsoft", "Google"]

#get a range of numbers from 1 to 11 for the months we're gathering data on
start_dates = [x+1 for x in range(11)]

limit = 1000 #the number of tweets collected per company per month
for company in companies:
    tweets = []
    for date_index, start_date in enumerate(start_dates):
        end_date = start_date + 1 #the end data is one month after the start date
        start_date = add_zero(start_date) #convert to str and add 0 to start if one digit
        end_date = add_zero(end_date) #same as above
        query = f"{company} lang:en until:2021-{end_date}-01 since:2021-{start_date}-01" #the query submitted to twitter
        for index, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            tweets.append([date_index+1, tweet.content]) #appends each tweet we get to the list with the month it's from
            if index == limit-1: #stop once the limit has been reached
                break
    tweets = transpose(tweets) #pandas wants them transposed
    tweet_df = pd.DataFrame(tweets, ['Month', 'Content'])
    tweet_df = tweet_df.transpose() #transpose the df to get them back to how they were
    tweet_df.to_csv(f'{company}.csv') #write to output file