import DataPrep
import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import nltk.corpus 

# Create feature vector - document term matrix
countV = CountVectorizer()
train_count = countV.fit_transform(DataPrep.train_news['statement'].values)

# Print training document term matrix statistics
def get_countVectorizer_stats(save_dir):
    with open(os.path.join(save_dir, 'count_vectorizer_stats.txt'), 'w') as f:
        f.write(f'Vocabulary Size: {train_count.shape[1]}\n')
        f.write(f'Vocabulary: {countV.vocabulary_}\n')
        f.write(f'Feature Names: {countV.get_feature_names_out()[:25]}\n')

# Create TF-IDF frequency features
tfidfV = TfidfTransformer()
train_tfidf = tfidfV.fit_transform(train_count)

def get_tfidf_stats(save_dir):
    with open(os.path.join(save_dir, 'tfidf_stats.txt'), 'w') as f:
        f.write(f'Train TF-IDF shape: {train_tfidf.shape}\n')
        f.write(f'First 10 TF-IDF feature vectors: {train_tfidf.A[:10]}\n')

# TF-IDF Vectorizer with n-grams
tfidf_ngram = TfidfVectorizer(stop_words='english', ngram_range=(1, 4), use_idf=True, smooth_idf=True)

# POS Tagging example (if required)
tagged_sentences = nltk.corpus.treebank.tagged_sents()
cutoff = int(.75 * len(tagged_sentences))
training_sentences = DataPrep.train_news['statement']

# Training POS tagger based on words (optional, if POS tagging is needed in your model)
def features(sentence, index):
    """ sentence: [w1, w2, ...], index: the index of the word """
    return {
        'word': sentence[index],
        'is_first': index == 0,
        'is_last': index == len(sentence) - 1,
        'is_capitalized': sentence[index][0].upper() == sentence[index][0],
        'is_all_caps': sentence[index].upper() == sentence[index],
        'is_all_lower': sentence[index].lower() == sentence[index],
        'prefix-1': sentence[index][0],
        'prefix-2': sentence[index][:2],
        'prefix-3': sentence[index][:3],
        'suffix-1': sentence[index][-1],
        'suffix-2': sentence[index][-2:],
        'suffix-3': sentence[index][-3:],
        'prev_word': '' if index == 0 else sentence[index - 1],
        'next_word': '' if index == len(sentence) - 1 else sentence[index + 1],
        'has_hyphen': '-' in sentence[index],
        'is_numeric': sentence[index].isdigit(),
        'capitals_inside': sentence[index][1:].lower() != sentence[index][1:]
    }

# Helper function to strip tags from tagged corpus
def untag(tagged_sentence):
    return [w for w, t in tagged_sentence]

# Using Word2Vec 
with open("glove.6B.50d.txt", "rb") as lines:
    w2v = {line.split()[0]: np.array(list(map(float, line.split()[1:])))
           for line in lines}

class MeanEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        # if a text is empty we should return a vector of zeros
        # with the same dimensionality as all the other vectors
        self.dim = len(next(iter(word2vec.values())))

    def fit(self, X, y):
        return self

    def transform(self, X):
        return np.array([
            np.mean([self.word2vec[w] for w in words if w in self.word2vec]
                    or [np.zeros(self.dim)], axis=0)
            for words in X
        ])
