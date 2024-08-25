from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.utils.fake_news_detector import detect_fake_news
from src.utils.web_crawler import fetch_article
app = FastAPI()

class ArticleInput(BaseModel):
    url: str

class ArticleOutput(BaseModel):
    title: str
    text: str
    is_fake: Optional[bool] = None
    confidence: Optional[float] = None

@app.get("/")
async def health() -> dict:
    """
    Root API endpoint to check the health of the service.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"messages": "Hello Hacx!"}


@app.post("/check-article/", response_model=ArticleOutput)
async def check_article(input_data: ArticleInput):
    try:
        article = fetch_article(input_data.url)
        detection_result = detect_fake_news(article['text'])
        article_output = ArticleOutput(
            title=article['title'],
            text=article['text'],
            is_fake=detection_result['label'] == "FAKE",
            confidence=detection_result['score']
        )
        return article_output
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))