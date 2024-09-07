from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import Annotated, Optional
from src.utils.LLMs.deBERTa_model import detect_fake_news, interpret_results
from src.utils.LLMs.gpt_model import get_gpt_response, parse_gpt_response
from src.utils.web_crawler import fetch_article
import os
from urllib.parse import unquote
from src.db.db_access import DatabaseAccessAzure
from dotenv import load_dotenv
from src.utils.OCR import azure_ocr_image_to_text, is_url_image


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
    return templates.TemplateResponse("main.html", {"request": request, "messages": "Hello Hacx"})
    # return {"messages": "Hello Hacx!"}


@app.post("/")
# @app.post("/check-article/", response_model=ArticleOutput)
async def check_article(request: Request, input_data: str = Form(...)):
    # input_data gets the URL link from the textbox
    try:
        # Decode any special characters in the URL
        url = unquote(input_data)

        if is_url_image(url):
            # The input URL is an image
            extracted_text = azure_ocr_image_to_text(url)
            print(extracted_text)
            article_text = extracted_text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ') \
                .replace('\xa0', ' ').replace('\u200b', ' ').replace('\u200e', ' ').replace('\u200f', ' ')
            article = {
                'title': 'Text Extracted from Image',
                'text': article_text
            }
        else:
            # The input URL is a web link
            article = fetch_article(url)
            article['text'] = article['text'].replace('\n', ' ').replace('\r', ' ').replace('\t', ' ') \
                .replace('\xa0', ' ').replace('\u200b', ' ').replace('\u200e', ' ').replace('\u200f', ' ')

        # Perform fake news detection, Layer 1 (ChatGPT)
        response = get_gpt_response(article['text'])
        gpt_response = response['choices'][0]['message']['content'].strip()
        interpretation, confidence, explanation = parse_gpt_response(gpt_response)

        if confidence == "Unknown" or confidence < 50:
            # Perform fake news detection, Layer 2 (Hugging Face LLM)
            detection_result = detect_fake_news(article['text'])
            interpretation = interpret_results(detection_result)
            confidence = max(detection_result.values())

        article_output = ArticleOutput(
            title=article['title'],
            explanation=explanation,
            interpretation=interpretation,
            confidence=confidence
        )

        # Uncomment the following lines to save data into the 'output_data' table
        # true = 0 if interpretation.lower() == "true" else 1
        # db.send("output_data", (article["text"], true))

        return templates.TemplateResponse('main.html', context={
            'request': request,
            'result': article_output,
            'input_data': article
        })

    except Exception as e:
        # Handle exceptions and display the error message on the frontend
        return templates.TemplateResponse('main.html', context={
            'request': request,
            'result': str(e),
            'input_data': {'url': url}
        })
