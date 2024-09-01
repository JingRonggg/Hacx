from newspaper import Article
from newsplease import NewsPlease
from newsplease.crawler.spiders.rss_crawler import RssCrawler
from newsplease.crawler.spiders.newsplease_spider import NewspleaseSpider
from newsplease.helper_classes.url_extractor import UrlExtractor

RssCrawler(helper=None, url='https://www.channelnewsasia.com/rss', config=None, ignore_regex=1)

def fetch_article2(url):
    article = NewsPlease.from_url(url)
    return{
        'title': print('title: ' + article.title),
        'description': print('description: ' + article.description),
        'maintext': print('maintext: ' + article.maintext),
        'authors': print('authors: '+ article.authors),
    }

def fetch_article(url):
    article = Article(url)
    article.download()
    article.parse()
    return {
        'title': article.title,
        'text': article.text,
        'authors': article.authors,
        'publish_date': article.publish_date,
        'top_image': article.top_image,
    }