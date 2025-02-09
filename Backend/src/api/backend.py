from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import Optional
from src.LLMs.Full_check_LLM import detect_fake_news_in_article
from src.utils.image_checking import process_url
from src.utils.web_crawler import fetch_articles
import os
from collections import Counter
from urllib.parse import unquote, urlparse
from src.db.db_access import DatabaseAccessAzure
from dotenv import load_dotenv
from src.db.testingDB import readtable
from src.db.testingDB import createinput, get_author
from src.LLMs.sentimental_analysis import sentimental_analysis
import json
import datetime

app = FastAPI()

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_NAME = os.getenv("SERVER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
SERVER_USERNAME = os.getenv("SERVER_USERNAME")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")

# Initialize Database Access
db = DatabaseAccessAzure(
    server_name=SERVER_NAME,
    database_name=DATABASE_NAME,
    username=SERVER_USERNAME,
    password=SERVER_PASSWORD
)

# Set the correct path for Jinja2 templates directory
templates = Jinja2Templates(directory="../Frontend")

# Set the correct path for static files directory
app.mount("/static", StaticFiles(directory="../static"), name="static")
app.add_middleware(GZipMiddleware)

class ArticleInput(BaseModel):
    url: str

class ArticleOutput(BaseModel):
    title: str
    explanation: str
    interpretation: str
    confidence: Optional[float] = None
    deepfake: Optional[float] = None
    sentiment: Optional[str] = None
    sentiment_explanation: Optional[str] = None
    disinformation: Optional[str] = None
    disinformation_explanation: Optional[str] = None
    target_Audience: Optional[str] = None


def get_domain_name(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def calculate_top_authors(data, top_n=6):
    author_counter = Counter()

    for entry in data:
        # entry[3] is 'interpretation', entry[11] is the 'url'
        if entry[2].lower() == 'fake':  # Only count fake news articles
            author = get_author(entry[10])
            
            # Increment the count for this domain
            author_counter[author] += 1

    # Return the top N domains as a dictionary (domain: count)
    top_authors = dict(author_counter.most_common(top_n))
    return top_authors


@app.get("/")
async def health(request: Request, page: int = 1, page_size: int = 5, category: Optional[str] = None):
    page = page if page else 1
    # Get the top authors for display
    top_authors = calculate_top_authors(readtable("output_data"))
    crawled_articles = readtable("input_data")

    # Base query for fetching articles
    query = "SELECT * FROM output_data"
    
    # If a category is selected, filter by category
    if category:
        query += f" WHERE interpretation = '{category}'"
    
    # Get the total number of articles (with or without category filter)
    total_articles = len(db.query(query))
    
    # Calculate the offset for pagination
    offset = (page - 1) * page_size

    # Apply pagination with OFFSET and FETCH NEXT (with or without category filter)
    paginated_query = f"{query} ORDER BY added_time DESC OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"
    db_outputdata_items = db.query(paginated_query)
    
    explanation_query = f"{query} ORDER BY added_time DESC"
    output_data = db.query(explanation_query)

    # Calculate the total number of pages
    total_pages = (total_articles + page_size - 1) // page_size

    # Prepare interpretation counts for chart display
    interpretation_counts = {
        "Fake": 0,
        "LIKELY TRUE": 0,
        "Real": 0,
        "Unclear": 0,
        "Unsure (Neutral)": 0
    }

    interpretation_counts2 = {}

    interpretation_data = db.query(
            "SELECT CAST(interpretation AS VARCHAR(MAX)), COUNT(*) FROM output_data GROUP BY CAST(interpretation AS VARCHAR(MAX))"
        )
    
    interpretation_data2 = db.query(
            "SELECT CAST(CONVERT(DATE, added_time) AS VARCHAR(MAX)), COUNT(*) FROM output_data WHERE CAST(interpretation AS VARCHAR(MAX)) = 'Fake' GROUP BY CONVERT(DATE, added_time);"
        )

    

    print(interpretation_data)  # Should display something like {"Fake": 1, "Real": 5, ...}
    print(interpretation_data2)  # Should display the time-based counts.

    for row in interpretation_data:
        if row[0] in interpretation_counts:
            interpretation_counts[row[0]] = row[1]
            

    for row in interpretation_data2:
        date = row[0]  # Assuming row[0] is the date
        count = row[1]  # Assuming row[1] is the count
        interpretation_counts2[date] = count

# # Iterate over the rows in interpretation_data2
#     for row in interpretation_data2:
#         # Extract the date and the label
#         date = row[0]  # Assuming row[0] is the date
#         label = row[1]  # Assuming row[1] is the label (e.g., 'Propaganda', 'Real', etc.)
#         print(date)
#         print(label)
#         # Only count fake news ('Propaganda')
        
#         # If the date is already in the dictionary, increment its count
#         if date in interpretation_counts2:
#             interpretation_counts2[date] += 1
#         else:
#             # If the date is not in the dictionary, add it with a count of 1
#             interpretation_counts2[date] = 1

    print(interpretation_counts2)

    return templates.TemplateResponse(
        "home.html", 
        {
            "request": request,
            "result": db_outputdata_items,
            "explanation_result" : output_data,
            "interpretationCounts": interpretation_counts,
            "interpretationCounts2": interpretation_counts2,
            "crawled": crawled_articles,
            "top_authors": top_authors,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "selected_category": category 
        }
    )

@app.post("/")
async def check_article(request: Request, input_data: str = Form(...), page: int = 1, page_size: int = 5, category: Optional[str] = None):
    try:
        # Process the URL and decode it
        url = unquote(input_data)

        # Check if the URL already exists in the input_data table
        url_exists = db.query(f"SELECT COUNT(*) FROM dbo.input_data WHERE url = '{url}'")

        # Process the URL to detect fake news
        article = process_url(url)
        
        print(article)
        
        # sentiment, sentiment_Explanation, disinformation, disinformation_Explanation, target_Audience = sentimental_analysis(article.get('text'))
    
        # article.sentiment = sentiment
        # article.sentiment_explanation = sentiment_Explanation
        # article.disinformation = disinformation
        # article.disinformation_explanation = disinformation_Explanation
        # article.target_Audience = target_Audience
        
        if (article.target_Audience != None):
            print("this is target audience" + article.target_Audience)
            # Insert the article into the input_data table if it doesn't exist
            if url_exists[0][0] == 0:
                author = get_domain_name(url) if article.authors == [] else article.authors[0]
                db.send("input_data", (article.title, article.text, author, None, url))
            # Handle article processing and database insertions based on `article` values here
            top_authors = calculate_top_authors(readtable("output_data"))
        else: 
            print(article)
            if hasattr(article, 'interpretation') and article.interpretation == "Propaganda":
                # Save the article to the output_data table
                output = (
                    article.title, article.explanation, article.interpretation, article.confidence, article.deepfake,
                    article.sentiment, article.sentiment_explanation, article.disinformation, article.disinformation_explanation,
                    article.target_Audience, url, datetime.datetime.now()
                )
                inputdata = (article.title, None, None, None, url)
                createinput("input_data", inputdata)
                createinput("output_data", output)
                return RedirectResponse(url='/', status_code=303)

            if hasattr(article, 'interpretation') and article.interpretation == "Not Propaganda":
                if(hasattr(article, 'text')):
                    article_output = detect_fake_news_in_article(article)
                # Save the article to the output_data table
                output = (
                    article.title, article.explanation, article.interpretation, article.confidence, article.deepfake,
                    article.sentiment, article.sentiment_explanation, article.disinformation, article.disinformation_explanation,
                    article.target_Audience, url, datetime.datetime.now()
                )
                inputdata = (article.title, None, None, None, url)
                createinput("input_data", inputdata)
                createinput("output_data", output)
                return RedirectResponse(url='/', status_code=303)

            if('deepfake' in article):
                article_output.deepfake = article['deepfake']

        article_output = detect_fake_news_in_article(article)
        # Save the processed article to the output_data table
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
            datetime.datetime.now()
        )

        createinput("output_data", output)
        
        interpretation_counts = {
            "Fake": 0,
            "LIKELY TRUE": 0,
            "Real": 0,
            "Unclear": 0,
            "Unsure (Neutral)": 0
        }


        interpretation_data = db.query(
            "SELECT CAST(interpretation AS VARCHAR(MAX)), COUNT(*) FROM output_data GROUP BY CAST(interpretation AS VARCHAR(MAX))"
        )


        # Redirect to maintain page, category, and pagination state
        return RedirectResponse(url=f"/?page={page}&category={category or ''}&page_size={page_size}", status_code=303)

    except Exception as e:
        top_authors = calculate_top_authors(readtable('output_data'))
        return templates.TemplateResponse('home.html', {
            'request': request,
            'result': f"Error: {str(e)}",
            'input_data': {'url': None},
            'top_authors': top_authors,
            'interpretationCounts': {"Fake": 0, "LIKELY TRUE": 0, "Real": 0, "Unclear": 0, "Unsure (Neutral)": 0},
            'page': page,
            'page_size': page_size,
            'total_pages': (len(db.query("SELECT * FROM output_data")) + page_size - 1) // page_size,
            'selected_category': category
        })

@app.get("/articles")
async def articles(request: Request):
    crawled_articles = readtable("input_data")
    return templates.TemplateResponse(
        "articles.html", 
        {"request": request, "crawled": crawled_articles}
    )

@app.post("/articles")
async def check_crawled_articles(request: Request):
    fetch_articles()

    return RedirectResponse(url="/articles", status_code=303)
    # return templates.TemplateResponse(
    #     "articles.html", 
    #     {"request": request, "crawled": crawled_articles}
    # )



@app.get("/get_articles_by_category")
async def get_articles_by_category(category: str, page: int = 1, page_size: int = 5):
    try:
        # Calculate the offset for pagination
        offset = (page - 1) * page_size

        # Query to fetch filtered articles by category with pagination
        query = """
            SELECT * FROM output_data 
            WHERE CAST(interpretation AS VARCHAR(MAX)) = ? 
            ORDER BY added_time DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """
        articles = db.query(query, (category, offset, page_size))

        # Format the articles into a list of dictionaries
        articles_list = []
        for article in articles:
            articles_list.append({
                "title": article[0],
                "explanation": article[1],
                "interpretation": article[2],
                "confidence": article[3],
                "deepfake": article[4],
                "sentiment_explanation": article[5],
                "target_Audience": article[6]
            })

        # Fetch total count of articles matching the category for pagination
        total_articles_query = """
            SELECT COUNT(*) FROM output_data WHERE CAST(interpretation AS VARCHAR(MAX)) = ?
        """
        total_articles = db.query(total_articles_query, (category,))[0][0]

        total_pages = (total_articles + page_size - 1) // page_size

        return {
            "articles": articles_list,
            "total_pages": total_pages,
            "current_page": page,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))