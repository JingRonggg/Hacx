import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
from urllib.parse import urljoin, urlparse
import re
from collections import deque
from datetime import datetime, timedelta

# Set the root URLs and output file path
root_urls = ["https://abcnews.go.com/", "https://www.channelnewsasia.com/", "https://www.straitstimes.com/"]
output_file = "output.json"

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

def crawl(limit=30):
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
    
    return save_to_json(results, output_file)

def save_to_json(data, filename):
    """Save data to a JSON file."""
    with open(filename, 'w') as file, open(filename, 'r+') as existing_file:
        # Load existing data to avoid duplicates across runs
        try:
            existing_data = json.load(existing_file)
            existing_urls = {entry['url'] for entry in existing_data}
        except json.JSONDecodeError:
            existing_data = []
            existing_urls = set()

        # Add only new results to the existing data
        new_data = [entry for entry in data if entry['url'] not in existing_urls]
        if new_data:
            existing_data.extend(new_data)
            json.dump(existing_data, file, indent=4)
            print(f"Data saved to {output_file}")
        else:
            print("No new data to add.")

def fetch_article():
    """Fetch articles from the URLs stored in the output.json file, excluding root URLs, and crawl data."""
    # Start crawling from the root URLs with a limit of 30 links
    print("Starting crawl...")
    crawled_data = crawl(limit=30)

    # Fetch and print the URLs stored in the JSON file
    try:
        with open(output_file, 'r') as file:
            existing_data = json.load(file)

        # Extract URLs and print them, excluding root URLs
        root_urls_set = set(root_urls)  # Convert root_urls list to a set for faster lookup
        urls = [entry['url'] for entry in existing_data]
        print("Fetched URLs (excluding root URLs) from the JSON file:")
        for url in urls:
            if url not in root_urls_set:  # Skip root URLs
                print(url)

    except FileNotFoundError:
        print("The output.json file was not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON from the output.json file.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Now you can call fetch_article to crawl and fetch all articles
fetch_article()