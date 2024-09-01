# Adapted from NishitP 

import os
import pandas as pd
import numpy as np
import nltk
from nltk.stem import SnowballStemmer
from nltk.stem.porter import PorterStemmer
import seaborn as sb
import matplotlib.pyplot as plt

#before reading the files, setup the working directory to point to project repo
#reading data files 
test_filename = 'reduced_test.csv'
train_filename = 'reduced_train.csv'
valid_filename = 'reduced_valid.csv'

train_news = pd.read_csv(train_filename)
test_news = pd.read_csv(test_filename)
valid_news = pd.read_csv(valid_filename)

#distribution of classes for prediction
def create_distribution(dataFile, save_dir):
    plot = sb.countplot(x='Label', data=dataFile, palette='hls', legend=False)
    plt.title('Class Distribution')
    plt.xlabel('Class')
    plt.ylabel('Count')
    # Save the plot
    plot_path = os.path.join(save_dir, f'{dataFile.name}_distribution.png')
    plt.savefig(plot_path)
    plt.clf()  # Clear the figure to avoid overlap in subsequent plots

    
eng_stemmer = SnowballStemmer('english')
stopwords = set(nltk.corpus.stopwords.words('english'))

#Stemming
def stem_tokens(tokens, stemmer):
    stemmed = []
    for token in tokens:
        stemmed.append(stemmer.stem(token))
    return stemmed

#process the data
def process_data(data,exclude_stopword=True,stem=True):
    tokens = [w.lower() for w in data]
    tokens_stemmed = tokens
    tokens_stemmed = stem_tokens(tokens, eng_stemmer)
    tokens_stemmed = [w for w in tokens_stemmed if w not in stopwords ]
    return tokens_stemmed


#creating ngrams
#unigram 
def create_unigram(words):
    assert type(words) == list
    return words

#bigram
def create_bigrams(words):
    assert type(words) == list
    skip = 0
    join_str = " "
    Len = len(words)
    if Len > 1:
        lst = []
        for i in range(Len-1):
            for k in range(1,skip+2):
                if i+k < Len:
                    lst.append(join_str.join([words[i],words[i+k]]))
    else:
        #set it as unigram
        lst = create_unigram(words)
    return lst

porter = PorterStemmer()

def tokenizer(text):
    return text.split()


def tokenizer_porter(text):
    return [porter.stem(word) for word in text.split()]