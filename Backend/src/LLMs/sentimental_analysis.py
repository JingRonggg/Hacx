import os
import requests
from dotenv import load_dotenv
import re

# Load environment variables from the .env file
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY2")  # Get the API key from the .env file
ENDPOINT = os.getenv("AZURE_END_POINT2")  # Get the endpoint from the .env file

# Update headers to include the API key (not endpoint)
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

# Function to get a response from the GPT model
def get_gpt_response(article_text):
    # Create the prompt for detecting fake news
    prompt = f"""
    You are a highly advanced AI with expertise in detecting disinformation. 
    Your task is to analyze the following article and provide an assessment of its sentiment and potential for disinformation. 
    First, determine the overall sentiment of the article and the emotions it conveys
    Second, based on the sentiment and the content, evaluate if the article shows signs of disinformation. 
    Consider factors like exaggerated claims, lack of evidence, or biased perspectives. 
    Provide a 1 line explanation of your assessment.
    With your analysis, provide me with the likely target audience of the article.
    Sentiment and Disinformation Assessment:
    Here is the article text:
    News article: {article_text}

    You should output your analysis in the following format:
    1. Overall Sentiment: [Sentiment classification]
    2. Explanation: [Brief explanation of the sentiment classification]
    3. Potential for Disinformation: [Disinformation classification]
    4. Explanation: [Brief explanation of the disinformation classification]
    5. Likely Target Audience: [Target audience of the article]

    Response:
    """

    role = """
    You are an advanced sentiment analysis AI,
    specialized in understanding and interpreting emotional tone in text.
    Your goal is to analyze the provided article and deliver a comprehensive sentiment analysis using logic, evidence, and critical analysis.
    """
    
    # Payload for the request
    payload = {
        "messages": [
            {"role": "system", "content": role},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "top_p": 0.95,
        "max_tokens": 2000
    }
    # Send request
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")
    

def parse_text(text):
    """
    Extracts and parses specific pieces of information from a formatted text string.

    The text is expected to be in a specific format with sections labeled as follows:
    1. Overall Sentiment: [sentiment]
    2. Explanation: [first explanation]
    3. Potential for Disinformation: [disinformation level]
    4. Explanation: [second explanation]
    5. Likely Target Audience: [target audience]

    Each section is expected to be on a new line and follows a specific pattern. The function 
    extracts and returns the sentiment, the first explanation, the potential for disinformation, 
    the second explanation, and the target audience from the text.

    Args:
        text (str): The input text string to be parsed. It should contain sections labeled 
                    as "Overall Sentiment", "Explanation", "Potential for Disinformation", 
                    and "Likely Target Audience" in the specified format.

    Returns:
        tuple: A tuple containing five elements:
            - sentiment (str): The overall sentiment extracted from the text. Defaults to "Unclear"
            if not found.
            - explanation1 (str): The first explanation extracted from the text. Defaults to "No explanation provided."
            if not found.
            - disinformation (str): The potential for disinformation extracted from the text. Defaults to "Unknown"
            if not found.
            - explanation2 (str): The second explanation extracted from the text. Defaults to "No explanation provided."
            if not found.
            - target_audience (str): The target audience extracted from the text. Defaults to "Not specified"
            if not found.
    """

    # Extract the overall sentiment
    sentiment_match = re.search(r"1\.\s*Overall Sentiment:\s*(.+)", text, re.IGNORECASE)
    sentiment = sentiment_match.group(1).strip() if sentiment_match else "Unclear"
    
    # Extract the first explanation
    explanation1_match = re.search(r"2\.\s*Explanation:\s*(.+?)(?=\n\d+\.\s*|$)", text, re.DOTALL)
    explanation1 = explanation1_match.group(1).strip() if explanation1_match else "No explanation provided."
    
    # Extract the potential for disinformation
    disinformation_match = re.search(r"3\.\s*Potential for Disinformation:\s*(.+)", text, re.IGNORECASE)
    disinformation = disinformation_match.group(1).strip() if disinformation_match else "Unknown"
    
    # Extract the second explanation
    explanation2_match = re.search(r"4\.\s*Explanation:\s*(.+?)(?=\n5\.\s*Likely Target Audience:|$)", text, re.DOTALL)
    explanation2 = explanation2_match.group(1).strip() if explanation2_match else "No explanation provided."
    
    # Extract the target audience
    target_audience_match = re.search(r"5\.\s*Likely Target Audience:\s*(.+)", text, re.IGNORECASE)
    target_audience = target_audience_match.group(1).strip() if target_audience_match else "Not specified"

    return sentiment, explanation1, disinformation, explanation2, target_audience

def sentimental_analysis(article_text):
    response = get_gpt_response(article_text)
    response = response['choices'][0]['message']['content'].strip()
    return parse_text(response)