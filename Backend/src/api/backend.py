from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import Annotated, Optional
from Backend.src.utils.deBERTa_model import detect_fake_news, interpret_results
from src.utils.web_crawler import fetch_article
from src.utils.gpt import get_gpt_response, parse_gpt_response
import os
from urllib.parse import unquote


app = FastAPI()
BASE_DIR = os.path.dirname(os.getcwd())

# Set the correct path for Jinja2 templates directory
templates = Jinja2Templates(directory="..\Frontend")
# Set the correct path for static files directory
app.mount(
    "/static", StaticFiles(directory="..\static"), name="static")
app.add_middleware(GZipMiddleware)


class ArticleInput(BaseModel):
    url: str


class ArticleOutput(BaseModel):
    title: str
    explanation: str
    is_fake: str
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
    # input_data gets the url link from the textbox
    try:
        # unquote() function decodes the special characters in URL
        article = fetch_article(unquote(input_data))
        article['text'] = article['text'].replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('\xa0', ' ').replace('\u200b', ' ').replace('\u200e', ' ').replace('\u200f', ' ')
        
        # Perform fake news detection, layer 1 (Chatgpt)
        response = get_gpt_response(article['text'])
        gpt_response = response['choices'][0]['message']['content'].strip()
        interpretation, confidence, explanation = parse_gpt_response(gpt_response)
        if confidence == "Unknown" or confidence < 50:

            # Perform fake news detection, layer 2 (hugging face LLM)
            detection_result = detect_fake_news(article['text'])
            interpretation = interpret_results(detection_result)
            confidence = max(detection_result.values())

        article_output = ArticleOutput(
            title=article['title'],
            explanation=explanation,
            is_fake=interpretation,
            confidence=confidence
        )
        return templates.TemplateResponse('main.html', context={'request': request, 'result': article_output, 'input_data': article})
        # return article_output
    except Exception as e:
        # display exception msg to frontend
        return templates.TemplateResponse('main.html', context={'request': request, 'result': e, 'input_data': article})

        # raise HTTPException(status_code=400, detail=str(e))
