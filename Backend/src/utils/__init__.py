from .deBERTa_model import detect_fake_news
from .web_crawler import fetch_article
from .gpt import get_gpt_response, parse_gpt_response
__all__ = ["get_gpt_response", "parse_gpt_response", "detect_fake_news", "interpret_results", "fetch_article"]
