# # utils/web_crawler.py

# import requests
# from bs4 import BeautifulSoup
# import time

# def fetch_content(url):
#     response = requests.get(url)
#     return response.text

# def parse_articles(html_content):
#     soup = BeautifulSoup(html_content, 'html.parser')
#     articles = []

#     # Example: Finding all article links on the page
#     for link in soup.find_all('a', href=True):
#         if "article" in link['href']:  # Filter to only news article URLs
#             articles.append(link['href'])

#     # Return only the latest 5 unique articles
#     return list(dict.fromkeys(articles))[:5]  # Remove duplicates and limit to 5

# def start_crawling(start_url, delay=60):
#     """
#     Continuously crawl the provided URL to detect new articles among the latest 5.

#     :param start_url: The root URL to crawl.
#     :param delay: Time in seconds between each crawl.
#     """
#     known_articles = []

#     while True:
#         html_content = fetch_content(start_url)
#         current_articles = parse_articles(html_content)
        
#         # Detect new articles by comparing with known articles
#         new_articles = [article for article in current_articles if article not in known_articles]
        
#         if new_articles:
#             print(f"New articles found: {len(new_articles)}")
#             for article in new_articles:
#                 print(f"New article: {article}")
            
#             # Update the known articles list to the latest 5 articles
#             known_articles = current_articles
        
#         else:
#             print("No new articles found.")
        
#         time.sleep(delay)  # Wait for the specified delay before the next crawl
