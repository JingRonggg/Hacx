from fastapi import Request
from collections import Counter
from src.db.testingDB import readtable
from src.db.testingDB import createinput, get_author
from src.db.db_access import DatabaseAccessAzure
import os


API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_NAME = os.getenv("SERVER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
SERVER_USERNAME = os.getenv("SERVER_USERNAME")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")

db = DatabaseAccessAzure(
    server_name=SERVER_NAME,
    database_name=DATABASE_NAME,
    username=SERVER_USERNAME,
    password=SERVER_PASSWORD
)

def calculate_top_authors(data, top_n=5):
    author_counter = Counter()

    for entry in data:
        # entry[3] is 'interpretation', entry[11] is the 'url'
        if entry[2].lower() == 'fake':  # Only count fake news articles
            author = get_author(entry[10])
            
            # Increment the count for this domain
            author_counter[author] += 1

    # Return the top N domains as a dictionary (domain: count)
    top_authors = dict(author_counter.most_common(top_n))
    return top_authors

# Helper function to prepare data for rendering the homepage
async def prepare_homepage_data(request: Request):
    top_authors = calculate_top_authors(readtable("output_data"))
    crawled_articles = readtable("input_data")
    
    interpretation_counts = {
        "Real": 0,
        "Propaganda": 0,
        "Unsure (Neutral)": 0
    }
    
    interpretation_data = db.query(
        "SELECT CAST(interpretation AS VARCHAR(MAX)), COUNT(*) FROM manual_data GROUP BY CAST(interpretation AS VARCHAR(MAX))"
    )

    for row in interpretation_data:
        if row[0] in interpretation_counts:
            interpretation_counts[row[0]] = row[1]

    return {
        "request": request,
        "interpretationCounts": interpretation_counts,
        "crawled": crawled_articles,
        "top_authors": top_authors
    }