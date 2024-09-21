import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin, urlparse
import re
from collections import deque
from datetime import datetime, timedelta
from src.db.testingDB import get_author
from src.db.testingDB import createinput
from src.utils.image_checking import process_url, fetch_article
from src.LLMs.Full_check_LLM import detect_fake_news_in_article
from src.LLMs.sentimental_analysis import sentimental_analysis

# Set the root URLs
root_urls = ["https://abcnews.go.com/", "https://www.channelnewsasia.com/", "https://www.straitstimes.com/"]

# Store visited URLs and the queue of URLs to process
visited_urls = set()
queue = deque(root_urls)  # Initialize the queue with multiple root URLs
results = []

def is_news_article(url):
    """Determine if a URL is a news article based on its structure and publication date."""
    parsed_url = urlparse(url)
    path = parsed_url.path

    # Common patterns found in news articles URLs
    patterns = [
        r'/\d{4}/\d{2}/\d{2}/',  # URL contains a date (e.g., /2024/09/07/)
        r'-\d{5,}',               # URL ends with a numeric ID (e.g., -113507800)
        r'/story/',               # URL contains "story" (e.g., /story?id=113507800)
        r'/news/',                # URL contains "news" (e.g., /news/world-123456)
        r'/article/',             # URL contains "article" (e.g., /article/123456)
        r'/politics/',            # URL contains "politics"
        r'/world/',               # URL contains "world"
        r'/singapore/',           # URL contains "singapore"
        r'/business/',            # URL contains "business"
        r'/sport/',               # URL contains "sport"
        r'/entertainment/',       # URL contains "entertainment"
        r'/environment/',         # URL contains "environment"
        r'/commentary/',          # URL contains "commentary"
    ]

    # Keywords that should exclude a URL (e.g., promotional links, external links)
    exclude_keywords = [
        'login', 'signup', 'profile', 'topic', 'myfeed', 'advertisement', 'promo', 
        'sponsored', 'campaign', 'utm_', 'hulu', 'netflix', 'disney', 'external',
        'redirect', 'referral', 'watch', 'shop', 'video'
    ]

    # Check if the URL matches any of the exclusion patterns
    for keyword in exclude_keywords:
        if keyword in url.lower():
            return False

    # Check if the URL matches any of the common news article patterns
    for pattern in patterns:
        if re.search(pattern, path):
            # Check if the article was published within the last 30 days
            match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', path)
            if match:
                year, month, day = map(int, match.groups())
                article_date = datetime(year, month, day)
                if article_date >= datetime.now() - timedelta(days=30):
                    return True
            return True

    return False

def fetch_url(url):
    """Fetch the HTML content of a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_html(html, base_url):
    """Parse HTML content and extract relevant data."""
    strainer = SoupStrainer('a', href=True)  # Only parse <a> tags with href attributes
    soup = BeautifulSoup(html, 'html.parser', parse_only=strainer)
    page_data = {
        'url': base_url,
        'links': []
    }
    
    # Extract all relevant links that are news articles
    for link in soup.find_all('a', href=True):
        href = link['href']
        absolute_url = urljoin(base_url, href)
        if is_news_article(absolute_url):
            page_data['links'].append(absolute_url)
    
    # Remove duplicate links
    page_data['links'] = list(set(page_data['links']))

    return page_data

def crawl(limit=10):
    """Crawl websites starting from the root URLs with a limit on the number of URLs."""
    global queue, visited_urls, results
    while queue and len(visited_urls) < limit:
        current_url = queue.popleft()  # Use popleft to dequeue from the front
        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)
        html = fetch_url(current_url)
        if html:
            page_data = parse_html(html, current_url)
            if page_data:
                results.append(page_data)
                # Add new links to the queue, respecting the limit
                for link in page_data['links']:
                    if link not in visited_urls and link not in queue and len(visited_urls) < limit:
                        queue.append(link)  # Use append to enqueue at the back

def fetch_articles():
    """Extract article URLs from the crawled data and process each article."""
    print("Starting crawl...")
    crawl(limit=10)
    root_urls_set = set(root_urls)
    article_list = []

    for entry in results:
        url = entry['url']
        if url not in root_urls_set:
            article_list.append(url)
            article = fetch_article(url)
        
            # Safely extract the first author or set to 'Unknown' if the list is empty 
            first_author = article["authors"][0] if article["authors"] else "Unknown"

            # Pass only the first author to createinput 
            p = createinput("input_data", (article["title"], article["text"], first_author, "", url))
            print(p)
            if p:
                article = process_url(url)
                # Perform fake news detection
                article_output = detect_fake_news_in_article(article)

                # Perform sentiment analysis
                sentiment, sentiment_Explanation, disinformation, disinformation_Explanation, target_Audience = sentimental_analysis(article['text'])
                article_output.sentiment = sentiment
                article_output.sentiment_explanation = sentiment_Explanation
                article_output.disinformation = disinformation
                article_output.disinformation_explanation = disinformation_Explanation
                article_output.target_Audience = target_Audience

                if('deepfake' in article):
                    article_output.deepfake = article['deepfake']
                
                output = (
                    article_output.title,
                    article_output.explanation,
                    article_output.interpretation,
                    article_output.confidence,
                    article_output.deepfake,
                    article_output.sentiment,
                    article_output.sentiment_explanation,
                    article_output.disinformation,
                    article_output.disinformation_explanation,
                    article_output.target_Audience,
                    url,
                    datetime.now()
                )
                # insert into manual_data table
                createinput("output_data", output)
    return article_list
