import os
import pandas as pd
import nltk
from nltk.stem import SnowballStemmer
from nltk.stem.porter import PorterStemmer
import seaborn as sb
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
from db.db_access import DatabaseAccessAzure

load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
SERVER_NAME = os.getenv("SERVER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
SERVER_USERNAME = os.getenv("SERVER_USERNAME")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")

# Load data from the pre_processed_data table using db_access
def load_data_from_db():
    # Initialize the database connection
    db = DatabaseAccessAzure(
        server_name = SERVER_NAME,  
        database_name = DATABASE_NAME,  
        username = SERVER_USERNAME,  
        password = SERVER_PASSWORD  
    )
    
    # Extract data from pre_processed_data table
    data = db.extract("pre_processed_data")  # Extract data from pre_processed_data table
    
    # Assuming the data has 'statement' and 'label' columns
    df = pd.DataFrame(data, columns=['id', 'statement', 'label'])
    
    # Use only 'statement' and 'label' columns
    return df[['statement', 'label']]

# Split the data into train, test, and validation sets
def split_data(data):
    train_data, temp_data = train_test_split(data, test_size=0.3, random_state=42, stratify=data['label'])
    test_data, valid_data = train_test_split(temp_data, test_size=0.333, random_state=42, stratify=temp_data['label'])
    return train_data, test_data, valid_data

# Load data from the database and split it
data = load_data_from_db()
train_news, test_news, valid_news = split_data(data)

# Distribution of classes for prediction
def create_distribution(dataFile, save_dir):
    plot = sb.countplot(x='label', data=dataFile, palette='hls', legend=False)
    plt.title('Class Distribution')
    plt.xlabel('Class')
    plt.ylabel('Count')
    # Save the plot
    plot_path = os.path.join(save_dir, f'{dataFile.name}_distribution.png')
    plt.savefig(plot_path)
    plt.clf()  # Clear the figure to avoid overlap in subsequent plots

# Stemming configuration
eng_stemmer = SnowballStemmer('english')
stopwords = set(nltk.corpus.stopwords.words('english'))

# Stemming function
def stem_tokens(tokens, stemmer):
    return [stemmer.stem(token) for token in tokens]

# Process the data
def process_data(data, exclude_stopword=True, stem=True):
    tokens = [w.lower() for w in data.split()]
    if stem:
        tokens = stem_tokens(tokens, eng_stemmer)
    if exclude_stopword:
        tokens = [w for w in tokens if w not in stopwords]
    return tokens

# Creating ngrams
# Unigram
def create_unigram(words):
    assert isinstance(words, list)
    return words

# Bigram
def create_bigrams(words):
    assert isinstance(words, list)
    skip = 0
    join_str = " "
    if len(words) > 1:
        lst = []
        for i in range(len(words) - 1):
            for k in range(1, skip + 2):
                if i + k < len(words):
                    lst.append(join_str.join([words[i], words[i + k]]))
    else:
        lst = create_unigram(words)
    return lst

# Porter Stemmer for tokenizer
porter = PorterStemmer()

def tokenizer(text):
    return text.split()

def tokenizer_porter(text):
    return [porter.stem(word) for word in text.split()]
