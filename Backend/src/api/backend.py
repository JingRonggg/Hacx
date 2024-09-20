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

def calculate_top_domains(data, top_n=5):
    domain_counter = Counter()

    for entry in data:
        # entry[3] is 'interpretation', entry[11] is the 'url'
        if entry[2].lower() == 'fake':  # Only count fake news articles
            # Extract domain from the URL
            parsed_url = urlparse(entry[10])
            domain = parsed_url.netloc  # Get the domain (e.g., 'abcnews.go.com')
            
            # Increment the count for this domain
            domain_counter[domain] += 1

    # Return the top N domains as a dictionary (domain: count)
    top_domains = dict(domain_counter.most_common(top_n))
    return top_domains

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

    # Populate chart_data from the output_data table
    for entry in data:
        chart_data["title"].append(entry[0] if entry[0] is not None else "No Title")
        chart_data["explanation"].append(entry[1] if entry[1] is not None else "No Explanation")
        chart_data["interpretation"].append(entry[2] if entry[2] is not None else "Unknown")
        chart_data["confidence"].append(entry[3] if entry[3] is not None else 0.0)
        chart_data["deepfake"].append(entry[4] if entry[4] is not None else 0.0)

    print(f"Chart Data: {chart_data}")

    # Calculate top domains for fake news articles
    top_domains = calculate_top_domains(data)

    # Initialize the interpretation counts for all categories from your output_data table
    interpretation_counts = {
        "Fake": 0,
        "LIKELY TRUE": 0,
        "Real": 0,
        "Unclear": 0,
        "Unsure (Neutral)": 0
    }

    # Fetch interpretation counts from the output_data table
    try:
        interpretation_data = db.query(
            "SELECT CAST(interpretation AS VARCHAR(MAX)), COUNT(*) FROM output_data GROUP BY CAST(interpretation AS VARCHAR(MAX))"
        )
        
        # Populate interpretation counts with new categories
        for row in interpretation_data:
            if row[0] in interpretation_counts:
                interpretation_counts[row[0]] = row[1]

        print(f"Interpretation Counts: {interpretation_counts}")

    except Exception as e:
        print(f"Failed to fetch interpretation data: {str(e)}")

    return templates.TemplateResponse(
        "home.html", 
        {
            "request": request, 
            "chartData": chart_data,  
            "top_domains": top_domains,  
            "interpretationCounts": interpretation_counts, 
            "crawled": crawled_articles  
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

        # Perform fake news detection and assign additional fields
        article_output = detect_fake_news_in_article(article)

        if 'deepfake' in article:
            article_output.deepfake = article['deepfake']

        # Save the processed article to the output_data table
        db.send("output_data", (
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
            url  # Add the URL to the output
        ))

        # **Re-fetch chart and article data after inserting the new article**
        data = db.readtable("output_data") or []
        chart_data = {
            "title": [],
            "explanation": [],
            "interpretation": [],
            "confidence": [],
            "deepfake": [],
        }

        # Update the chart data from the database
        for entry in data:
            chart_data["title"].append(entry[0] if entry[0] is not None else "No Title")
            chart_data["explanation"].append(entry[1] if entry[1] is not None else "No Explanation")
            chart_data["interpretation"].append(entry[2] if entry[2] is not None else "Unknown")
            chart_data["confidence"].append(entry[3] if entry[3] is not None else 0.0)
            chart_data["deepfake"].append(entry[4] if entry[4] is not None else 0.0)
        
        # Calculate top domains for fake news articles
        top_domains = calculate_top_domains(data)

        # Fetch interpretation counts from the output_data table and handle new categories
        interpretation_counts = {
            "Fake": 0,
            "LIKELY TRUE": 0,
            "Real": 0,
            "Unclear": 0,
            "Unsure (Neutral)": 0
        }

        # Fetch interpretation counts from the database
        interpretation_data = db.query(
            "SELECT CAST(interpretation AS VARCHAR(MAX)), COUNT(*) FROM output_data GROUP BY CAST(interpretation AS VARCHAR(MAX))"
        )
        
        for row in interpretation_data:
            if row[0] in interpretation_counts:
                interpretation_counts[row[0]] = row[1]

        # Now return the updated template with both the article and chart data
        return templates.TemplateResponse('home.html', {
            'request': request,
            'result': article_output,  # Article that was just added
            'input_data': article,  # Original article data
            'chartData': chart_data,  # Updated chart data
            'top_domains': top_domains,  # Updated top domains
            'interpretationCounts': interpretation_counts  # Updated interpretation counts with new categories
        })

    except Exception as e:
        print(f"Error while processing article: {str(e)}")
        return templates.TemplateResponse('home.html', {
            'request': request,
            'result': f"Error: {str(e)}",
            'input_data': {'url': None},
            'interpretationCounts': {"Fake": 0, "LIKELY TRUE": 0, "Real": 0, "Unclear": 0, "Unsure (Neutral)": 0},
            'top_domains': {}
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