from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
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
templates = Jinja2Templates(directory="..\Frontend")

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
    data = readtable("output_data")
    crawled_articles = readtable("input_data")

    chart_data = { 
        "title": [], 
        "explanation": [], 
        "interpretation": [], 
        "confidence": [], 
        "deepfake": [], 
        "sentiment": [], 
        "sentiment_explanation": [], 
        "disinformation": [], 
        "disinformation_explanation": [], 
        "target_audience": [],
        "url": []
        } 
    
    authors = []

    for entry in data: 
        chart_data["title"].append(entry[0]) 
        chart_data["explanation"].append(entry[1])
        chart_data["interpretation"].append(entry[2])
        chart_data["confidence"].append(entry[3])
        chart_data["deepfake"].append(entry[4])
        chart_data["sentiment"].append(entry[5])
        chart_data["sentiment_explanation"].append(entry[6]) 
        chart_data["disinformation"].append(entry[7])
        chart_data["disinformation_explanation"].append(entry[8])
        chart_data["target_audience"].append(entry[9])
        
        # Extract domain and update the counter
        if entry[2].lower() == "fake":
            author = get_author(entry[10])
            authors.append(author)

        chart_data["url"].append(entry[10])

        author_counter = Counter(authors)
        top_authors = dict(author_counter.most_common(5))

    return templates.TemplateResponse(
        "home.html", 
        {
            "request": request,
            "chartData": chart_data,
            "crawled": crawled_articles,
            "top_authors": top_authors
        }
    )

@app.post("/")
async def check_article(request: Request, input_data: str = Form(...)):
    try:
        url = unquote(input_data)
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
            

            return templates.TemplateResponse('home.html', {
                'request': request,
                'result': article,
                'input_data': {'url': url},
                'top_authors': top_authors
            })

        if hasattr(article, 'interpretation') and article.interpretation == "Not Propaganda":

            return templates.TemplateResponse('home.html', {
                'request': request,
                'result': article,
                'input_data': {'url': url},
                'top_authors': top_authors
            })

        # Perform fake news detection
        article_output = detect_fake_news_in_article(article)

        if 'deepfake' in article:
            article_output.deepfake = article['deepfake']

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

        return templates.TemplateResponse('home.html', {
            'request': request,
            'result': article_output,
            'input_data': article,
            'top_authors': top_authors
        })

    except Exception as e:
        top_authors = calculate_top_authors(readtable('output_data'))
        return templates.TemplateResponse('home.html', {
            'request': request,
            'result': str(e),
            'input_data': {'url': None},
            'top_authors': top_authors
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

@app.post("/get_related_articles")
async def get_related_articles(author: str):
    try:
        # Assuming your `readtable` function can fetch all articles
        articles = readtable("input_data")  # Example table storing article info

        related_articles = []
        for entry in articles:
            article_author = get_author(entry[10])  # Example: get author using entry index 10
            if article_author == author:
                related_articles.append({
                    "title": entry[0],  # Example: title
                    "url": entry[10]   # Example: URL
                })

        return {"articles": related_articles}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
