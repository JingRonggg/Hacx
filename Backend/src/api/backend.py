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
from urllib.parse import unquote
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
    }
    
    for entry in data:
        chart_data["title"].append(entry[1])
        chart_data["explanation"].append(entry[2])
        chart_data["interpretation"].append(entry[3])
        chart_data["confidence"].append(entry[4])
        chart_data["deepfake"].append(entry[5])

    return templates.TemplateResponse(
        "home.html", 
        {"request": request, "chartData": chart_data, "crawled": crawled_articles}
    )

@app.post("/")
async def check_article(request: Request, input_data: str = Form(...)):
    try:
        url = unquote(input_data)
        article = process_url(url)

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
            # insert into manual_data table
            createinput("output_data", output)
            
            return templates.TemplateResponse('home.html', {
                'request': request,
                'result': article,
                'input_data': {'url': url}
            })
        
        
        if hasattr(article, 'interpretation') and article.interpretation == "Not Propaganda":
            return templates.TemplateResponse('home.html', context={
                'request': request,
                'result': article,
                'input_data': {'url': url}
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
        # insert into manual_data table
        createinput("output_data", output)

        # return templates.TemplateResponse('home.html', context={
        return templates.TemplateResponse('home.html', {
            'request': request,
            'result': article_output,
            'input_data': article
        })

    except Exception as e:
        return templates.TemplateResponse('home.html', {
            'request': request,
            'result': str(e),
            'input_data': {'url': None}
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