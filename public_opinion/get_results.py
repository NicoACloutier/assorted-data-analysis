def main():
    from transformers import pipeline
    import pandas as pd
    from statistics import mean, stdev
    
    companies = ['Google', 'Tesla', 'Microsoft']
    months = [x+1 for x in range(11)]
    classifier = pipeline(task='sentiment-analysis') #nlp model that classifies text as either positive or negative
    
    output_df = pd.DataFrame() #initialize the final dataframe
    output_df['Months'] = months #add months
    
    for company in companies:
        tweet_df = pd.read_csv(f'{company}.csv') #read the raw twitter data
        mean_list = [] #list of means
        stdev_list = [] #list of standard deviations
        for month in months:
            month_tweets = tweet_df.loc[tweet_df['Month'] == month] #get all rows that correspond to a certain month
            scores = classifier(month_tweets['Content'].to_list()) #create a list of scores
            
            #the next three lines put scores on a scale from 0 (negative) to 1 (positive)
            pos_scores = [item['score'] for item in scores if item['label'] == 'POSITIVE']
            neg_scores = [1-item['score'] for item in scores if item['label'] == 'NEGATIVE']
            scores = pos_scores + neg_scores
            
            mean_score = mean(scores) #get the mean score
            score_stdev = stdev(scores) #get the standard deviation
            mean_list.append(mean_score) #add the mean score to the list
            stdev_list.append(score_stdev) #add the standard deviation to the list
        output_df[f'{company} Mean'] = mean_list #add new column to df with means for each month
        output_df[f'{company} Standard Deviation'] = stdev_list #do the same as above with standard deviations
    
    output_df.to_csv('final_data.csv') #write the ouput to a csv file

if __name__ == '__main__':
    main()