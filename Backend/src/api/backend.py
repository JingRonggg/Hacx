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
            # createinput("output_data", )
            
            return templates.TemplateResponse('home.html', context={
                'request': request,
                'result': article,
                'input_data': {'url': url}
            })
        # Perform fake news detection
        article_output = detect_fake_news_in_article(article)
        if('deepfake' in article):
            article_output.deepfake = article['deepfake']
            
        # Uncomment the following lines to save data into the 'output_data' table
        # true = 0 if interpretation.lower() == "true" else 1
        # db.send("output_data", (article["text"], true))
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