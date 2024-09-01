import requests
from bs4 import BeautifulSoup
import time

def fetch_headlines(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = [item.get_text(strip=True) for item in soup.find_all('h1')]
    return headlines


def continuous_crawl_and_check(url, interval=5):
    while True:
        try:
            headlines = fetch_headlines(url)
            print(headlines)
        except Exception as e:
            print(f"An error occurred: {e}")
        time.sleep(interval)

news_url = "https://www.straitstimes.com/"
continuous_crawl_and_check(news_url)
