# from .web_crawler import fetch_article
from .fake_news_detector import load_model, check_fake_news, interpret_results

__all__ = ["load_model", "check_fake_news", "interpret_results"]
