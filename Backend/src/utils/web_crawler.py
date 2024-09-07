import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
from urllib.parse import urljoin, urlparse
import re
from newsplease import NewsPlease  # Import NewsPlease

# Set the root URL and output file path
root_url = "https://www.channelnewsasia.com/"
output_file = "output.json"

# Store visited URLs and the queue of URLs to process
visited_urls = set()
queue = [root_url]
results = []


def is_news_article(url):
    """Determine if a URL is a news article based on its structure."""
    parsed_url = urlparse(url)
    path = parsed_url.path

    # Check if the URL contains a numeric ID at the end, which is typical for news articles
    article_id_match = re.search(r'-\d+$', path)

    # Ensure the URL path does not contain terms like 'profile', 'login', 'signup', etc.
    if not article_id_match or any(segment in path for segment in ['profile', 'login', 'signup', 'myfeed', 'topic']):
        return False

    # Additional check to ensure the URL structure is consistent with a news article
    is_valid_path = (
        "/world/" in path or
        "/asia/" in path or
        "/singapore/" in path or
        "/business/" in path or
        "/sport/" in path or
        "/commentary/" in path or
        "/environment/" in path or
        "/entertainment/" in path
    )

    return bool(article_id_match and is_valid_path)


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
    """Parse HTML content and extract relevant news article data."""
    strainer = SoupStrainer(
        'a', href=True)  # Only parse <a> tags with href attributes
    soup = BeautifulSoup(html, 'html.parser', parse_only=strainer)
    page_data = {
        'url': base_url,
        'title': None,
        'author': None,
        'main_text': None,
        'image': None,
        'date_publish': None,
        'links': []
    }

    # Extract all relevant links that are news articles
    for link in soup.find_all('a', href=True):
        href = link['href']
        absolute_url = urljoin(base_url, href)
        if is_news_article(absolute_url):
            page_data['links'].append(absolute_url)

    # Use NewsPlease to extract article information
    article_data = NewsPlease.from_url(base_url)
    if article_data:
        page_data['title'] = article_data.title
        page_data['author'] = article_data.authors if article_data.authors else 'No Author'
        page_data['main_text'] = article_data.maintext
        page_data['image'] = article_data.image_url
        # Convert datetime to string for JSON serialization
        if article_data.date_publish:
            page_data['date_publish'] = article_data.date_publish.isoformat()

    return page_data


def crawl(url, limit=10):
    """Crawl a website starting from the root URL with a limit on the number of URLs."""
    global queue, visited_urls, results
    while queue and len(visited_urls) < limit:
        current_url = queue.pop(0)
        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)
        html = fetch_url(current_url)
        if html:
            page_data = parse_html(html, current_url)
            results.append(page_data)
            # Add new links to the queue, respecting the limit
            for link in page_data['links']:
                if link not in visited_urls and len(visited_urls) < limit:
                    queue.append(link)

    return results


def save_to_json(data, filename):
    """Save data to a JSON file."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    # Start crawling from the root URL with a limit of 10 links
    print("Starting crawl...")
    crawled_data = crawl(root_url, limit=10)
    print("Crawl completed.")

    # Save the output to a JSON file
    save_to_json(crawled_data, output_file)
    print(f"Data saved to {output_file}")


# from newspaper import Article
# from newsplease import NewsPlease
# from newsplease.crawler.spiders.rss_crawler import RssCrawler
# from newsplease.crawler.spiders.newsplease_spider import NewspleaseSpider
# from newsplease.helper_classes.url_extractor import UrlExtractor

# RssCrawler(helper=None, url='https://www.channelnewsasia.com/rss', config=None, ignore_regex=1)

# def fetch_article2(url):
#     article = NewsPlease.from_url(url)
#     return{
#         'title': print('title: ' + article.title),
#         'description': print('description: ' + article.description),
#         'maintext': print('maintext: ' + article.maintext),
#         'authors': print('authors: '+ article.authors),
#     }

# def fetch_article(url):
#     article = Article(url)
#     article.download()
#     article.parse()
#     return {
#         'title': article.title,
#         'text': article.text,
#         'authors': article.authors,
#         'publish_date': article.publish_date,
#         'top_image': article.top_image,
#     }