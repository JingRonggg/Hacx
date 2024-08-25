from transformers import pipeline


def detect_fake_news(text):
    classifier = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-fake-news-detection")
    result = classifier(text)
    return result[0]  # e.g., {'label': 'REAL', 'score': 0.99}
