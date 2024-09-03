from .LLMs.deBERTa_model import detect_fake_news, interpret_results
from .web_crawler import fetch_article
from .LLMs.gpt_model import get_gpt_response, parse_gpt_response

__all__ = ["get_gpt_response", "parse_gpt_response", "detect_fake_news", "interpret_results", "fetch_article"]
