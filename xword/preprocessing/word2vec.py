from gensim import models
import pandas as pd

#Train word2vec model

def main():
    df = pd.read_csv('..\\data\\xword.csv')
    df['Answer'] = df['Answer'].astype(str)
    df['Clue'] = df['Clue'].astype(str)
    text = list(df['Answer']) + list(df['Clue'])

    model = models.Word2Vec(sentences=text, vector_size=48, window=5, min_count=1, workers=5)
    model.save("word2vec.model")
    
if __name__ == '__main__':
    main()
