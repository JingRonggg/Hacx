from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.utils.fake_news_detector import load_model, check_fake_news, interpret_results
# from src.utils.web_crawler import fetch_article
app = FastAPI()

class NewsItem(BaseModel):
    text: str

class ArticleOutput(BaseModel):
    title: str
    text: str
    is_fake: Optional[bool] = None
    confidence: Optional[float] = None

@app.on_event("startup")
async def startup_event():
    load_model()

@app.get("/")
async def health() -> dict:
    """
    Root API endpoint to check the health of the service.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"messages": "Hello Hacx!"}


@app.post("/check_news")
async def check_news(news_item: NewsItem):
    try:
        scores = check_fake_news(news_item.text)
        interpretation = interpret_results(scores)
        return {
            "scores": scores,
            "interpretation": interpretation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))