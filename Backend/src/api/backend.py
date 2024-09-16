from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import Annotated, Optional
from src.LLMs.Full_check_LLM import detect_fake_news_in_article
from src.utils.image_checking import process_url
from src.utils.web_crawler import fetch_articles
import os
from urllib.parse import unquote
from src.db.db_access import DatabaseAccessAzure
from dotenv import load_dotenv
from src.utils.image_checking import process_url
from src.db.testingDB import readtable
from src.db.testingDB import createinput
from src.LLMs.sentimental_analysis import sentimental_analysis

app = FastAPI()
BASE_DIR = os.path.dirname(os.getcwd())

load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_NAME = os.getenv("SERVER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
SERVER_USERNAME = os.getenv("SERVER_USERNAME")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")

# Initialize Database Access
db = DatabaseAccessAzure(
    server_name = SERVER_NAME,  
    database_name = DATABASE_NAME,  
    username = SERVER_USERNAME,  
    password = SERVER_PASSWORD
)

# Set the correct path for Jinja2 templates directory
templates = Jinja2Templates(directory="..\Frontend")
# Set the correct path for static files directory
app.mount(
    "/static", StaticFiles(directory="..\static"), name="static")
app.add_middleware(GZipMiddleware)

class ArticleInput(BaseModel):
    url: str

class ImageURL(BaseModel):
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
    """
    Root API endpoint to check the health of the service.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    # loads the things from the database 
    crawled_articles = readtable("input_data")
    return templates.TemplateResponse("home.html", {"request": request, "crawled": crawled_articles})
    # return {"messages": "Hello Hacx!"}

@app.post("/")
# async def check_article(request: Request):
async def check_article(request: Request, input_data: str = Form(...)):

    try:
        # Decode any special characters in the URL
        url = unquote(input_data)
        # Process the URL to extract the article text
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
            article.target_Audience
            )
            print(output)
            # insert into manual_data table
            # createinput("manual_data", output)
            
            return templates.TemplateResponse('home.html', context={
                'request': request,
                'result': article,
                'input_data': {'url': url}
            })
        # Perform fake news detection
        article_output = detect_fake_news_in_article(article)

        # Perform sentiment analysis
        sentiment, sentiment_Explanation, disinformation, disinformation_Explanation, target_Audience = sentimental_analysis(article['text'])
        article_output.sentiment = sentiment
        article_output.sentiment_explanation = sentiment_Explanation
        article_output.disinformation = disinformation
        article_output.disinformation_explanation = disinformation_Explanation
        article_output.target_Audience = target_Audience

        if('deepfake' in article):
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
            article_output.target_Audience
        )
        print(output)
        # insert into manual_data table
        # createinput("manual_data", output)

        return templates.TemplateResponse('home.html', context={
            'request': request,
            'result': article_output,
            'input_data': article
        })

    except Exception as e:
        # Handle exceptions and display the error message on the frontend
        return templates.TemplateResponse('home.html', context={
            'request': request,
            'result': str(e),
            'input_data': {'url': None}
        })


@app.get("/articles")
async def articles(request: Request):
    # loads the articles from the database 
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