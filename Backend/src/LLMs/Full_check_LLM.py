from src.LLMs.deBERTa_model import detect_fake_news, interpret_results
from src.LLMs.gpt_model import get_gpt_response, parse_gpt_response
from pydantic import BaseModel
from typing import Optional

class ArticleOutput(BaseModel):
    title: str
    explanation: str
    interpretation: str
    confidence: Optional[float] = None


def detect_fake_news_in_article(article):
    """
    Detects fake news in a given article by using two layers of detection:
    Layer 1: ChatGPT for initial detection
    Layer 2: Hugging Face LLM for further verification if needed

    Parameters:
        article (dict): A dictionary containing the article's title and text. 
                        Example: {'title': 'Example Title', 'text': 'Example text of the article'}

    Returns:
        ArticleOutput: An instance of the ArticleOutput class with the detection results.
    """
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

    return article_output
