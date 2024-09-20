from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import Optional
from src.LLMs.Full_check_LLM import detect_fake_news_in_article
from src.utils.image_checking import process_url
from src.utils.web_crawler import fetch_articles
import os
from collections import Counter
from urllib.parse import unquote, urlparse
from src.db.db_access import DatabaseAccessAzure
from dotenv import load_dotenv
from src.db.testingDB import readtable
from src.db.testingDB import createinput, get_author
from src.LLMs.sentimental_analysis import sentimental_analysis
import json

app = FastAPI()

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_NAME = os.getenv("SERVER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
SERVER_USERNAME = os.getenv("SERVER_USERNAME")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")

# Initialize Database Access
db = DatabaseAccessAzure(
    server_name=SERVER_NAME,
    database_name=DATABASE_NAME,
    username=SERVER_USERNAME,
    password=SERVER_PASSWORD
)

# Set the correct path for Jinja2 templates directory
templates = Jinja2Templates(directory="../Frontend")

# Set the correct path for static files directory
app.mount("/static", StaticFiles(directory="../static"), name="static")
app.add_middleware(GZipMiddleware)

class ArticleInput(BaseModel):
    url: str

class ArticleOutput(BaseModel):
    title: str
    explanation: str
    interpretation: str
    confidence: Optional[float] = None
    deepfake: Optional[float] = None
    sentiment: Optional[str] = None
    sentiment_explanation: Optional[str] = None
    disinformation: Optional[str] = None
    disinformation_explanation: Optional[str] = None
    target_Audience: Optional[str] = None

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

@app.get("/")
async def health(request: Request):
    top_authors = calculate_top_authors(readtable("output_data"))
    crawled_articles = readtable("input_data")
    db_outputdata_items = readtable("output_data")


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
    # return templates.TemplateResponse('home.html', {
        #     'request': request,
        #     'result': article_output,
        #     'input_data': article,
        #     'top_authors': top_authors,
        #     'interpretationCounts': interpretation_counts
        # })

    return templates.TemplateResponse(
        "home.html", 
        {
            "request": request,
            "result": db_outputdata_items,
            "interpretationCounts": interpretation_counts,
            "crawled": crawled_articles,
            "top_authors": top_authors
        }
    )

@app.post("/")
async def check_article(request: Request, input_data: str = Form(...)):
    try:
        # Process the URL and decode it
        url = unquote(input_data)
        
        # Check if the URL already exists in the input_data table
        url_exists = db.query(f"SELECT COUNT(*) FROM dbo.input_data WHERE url = '{url}'")

        if url_exists[0][0] == 0:
            # Insert the URL into the input_data table if it doesn't exist
            db.send("input_data", (None, None, None, None, url))  # Assuming input_data has these fields

        # Process the URL to detect fake news
        article = process_url(url)
        top_authors = calculate_top_authors(readtable("output_data"))

        if hasattr(article, 'interpretation') and article.interpretation == "Propaganda":
            # send output to db table
            output = (
                article.title,
                article.explanation,
                article.interpretation,
                article.confidence,
                article.deepfake,
                article.sentiment,
                article.sentiment_explanation,
                article.disinformation,
                article.disinformation_explanation,
                article.target_Audience, 
                url
            )
            createinput("output_data", output)

            return RedirectResponse(url = "/", status_code=303)

            # return templates.TemplateResponse('home.html', {
            #     'request': request,
            #     'result': article,
            #     'input_data': {'url': url},
            #     "top_authors": top_authors
            # })

        if hasattr(article, 'interpretation') and article.interpretation == "Not Propaganda":
            return RedirectResponse(url = "/", status_code=303)

            # return templates.TemplateResponse('home.html', context={
            #     'request': request,
            #     'result': article,
            #     'input_data': {'url': url},
            #     'top_authors': top_authors
            # })

        # Perform fake news detection
        article_output = detect_fake_news_in_article(article)

        if 'deepfake' in article:
            article_output.deepfake = article['deepfake']

        # Save the processed article to the output_data table
        output = (
            article_output.title,
            article_output.explanation,
            article_output.interpretation,
            article_output.confidence,
            article_output.deepfake,
            article_output.sentiment,
            article_output.sentiment_explanation,
            article_output.disinformation,
            article_output.disinformation_explanation,
            article_output.target_Audience,
            url
        )
        createinput("output_data", output)

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
        
        print(f"type article output: {type(article_output)}")
        print(f"article output: {article_output}")

        return RedirectResponse(url = "/", status_code=303)
        # return templates.TemplateResponse('home.html', {
        #     'request': request,
        #     'result': article_output,
        #     'input_data': article,
        #     'top_authors': top_authors,
        #     'interpretationCounts': interpretation_counts
        # })

    except Exception as e:
        top_authors = calculate_top_authors(readtable('output_data'))
        return templates.TemplateResponse('home.html', {
            'request': request,
            'result': f"Error: {str(e)}",
            'input_data': {'url': None},
            'top_authors': top_authors,
            'interpretationCounts': {"Real": 0, "Propaganda": 0, "Unsure (Neutral)": 0}
        })

@app.get("/articles")
async def articles(request: Request):
    crawled_articles = readtable("input_data")
    return templates.TemplateResponse(
        "articles.html", 
        {"request": request, "crawled": crawled_articles}
    )

@app.post("/articles")
async def check_crawled_articles(request: Request):
    urls = fetch_articles()
    crawled_articles = readtable("input_data")

    return templates.TemplateResponse(
        "articles.html", 
        {"request": request, "crawled": crawled_articles}
    )
