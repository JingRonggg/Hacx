from src.utils.OCR import azure_ocr_image_to_text, is_url_image
from src.utils.web_crawler import fetch_article

def process_url(url):
    """
    Processes a given URL to extract and clean text either from an image or a web page.

    Parameters:
    - url (str): The URL to be processed.

    Returns:
    - dict: A dictionary with 'title' and 'text' keys.
    """
    def clean_text(text):
        """Helper function to clean text by replacing unwanted characters."""
        return text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ') \
            .replace('\xa0', ' ').replace('\u200b', ' ').replace('\u200e', ' ').replace('\u200f', ' ')

    if is_url_image(url):
        # The input URL is an image
        extracted_text = azure_ocr_image_to_text(url)
        article_text = clean_text(extracted_text)
        article = {
            'title': 'Text Extracted from Image',
            'text': article_text
        }
    else:
        # The input URL is a web link
        article = fetch_article(url)
        article['text'] = clean_text(article['text'])
    
    return article
