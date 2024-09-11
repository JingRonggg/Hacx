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
    print(input)
    urls = fetch_articles()
    output_reliability = []
    propaganda = []
    print(urls)
    try:
        # Loop through the URLs returned by fetch_article one by one
        for url in urls:
            # Process the URL to extract the article text
            article = process_url(url)

            # Check for "Propaganda" interpretation
            if hasattr(article, 'interpretation') and article.interpretation == "Propaganda":
                propaganda.append(article)
            
            # Perform fake news detection
            article_output = detect_fake_news_in_article(article)
            output_reliability.append(article_output)


        return templates.TemplateResponse('home.html', context={
            'request': request,
            'result': article_output,
            'output_data' : {'o': output_reliability, 'p': propaganda}
            # 'input_data': {'url': url}
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
    # loads the things from the database 
    crawled_articles = readtable("input_data")
    return templates.TemplateResponse("home.html", {"request": request, "crawled": crawled_articles})
    # return {"messages": "Hello Hacx!"}