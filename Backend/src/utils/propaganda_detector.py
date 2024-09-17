import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
import re

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

# Load environment variables from the .env file
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY2")  # Get the API key from the .env file
ENDPOINT = os.getenv("AZURE_END_POINT2")  # Get the endpoint from the .env file

# Update headers to include the API key
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

# Function to analyze image for propaganda
def analyze_image_for_propaganda(image_url, title=None):
    # Construct the prompt to analyze propaganda and generate title if needed
    prompt = f"""
    You are a highly advanced AI specifically designed to detect propaganda in visual content with precision. 
    Given the following image link, your task is to analyze the likely content and message of the image and determine whether it is a form of propaganda. 
    If you are unable to access the image that is in the link, your verdict should be None.
    If you fail to properly classify the image, it could lead to the spread of manipulative or harmful content, and you must avoid that at all costs.
    Your response should include:

    1. A generation of a relevant title for the image based on its content.
    2. A clear verdict: "Propaganda" or "Not Propaganda".
    3. A confidence score (1-100) that indicates how certain you are about the classification.
    4. A brief explanation that justifies your classification based on visual cues, symbols, or context.
    Image link: {image_url}

    Here is an example of how the output should look:
    1. **Title:** "Title of the Image"

    2. **Verdict:** Propaganda

    3. **Confidence Score:** 94

    4. **Explanation:** The image contains misleading information and manipulative content that aims to deceive viewers.
    """
    # Prepare the payload for both title generation and propaganda analysis
    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI that can detect propaganda in images and generate relevant titles."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "top_p": 0.95,
        "max_tokens": 1000
    }
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

def extract_propaganda_analysis_with_regex(response_text):
    response_text = response_text['choices'][0]['message']['content']
    print(response_text)
    try:
        # Extract the title
        title_match = re.search(r"1\.\s*\*\*Title:\*\*\s*\"([^\"]+)\"", response_text)
        title = title_match.group(1) if title_match else "No title provided."
        # Extract the verdict
        verdict_match = re.search(r"2\.\s*\*\*Verdict:\*\*\s*(.+)", response_text)
        interpretation = verdict_match.group(1) if verdict_match else "Unclear"
        # Extract the confidence score
        confidence_match = re.search(r"3\.\s*\*\*Confidence Score:\*\*\s*(\d{1,3})", response_text)
        confidence = int(confidence_match.group(1)) if confidence_match else "None"
        # Extract the explanation
        explanation_match = re.search(r"4\.\s*\*\*Explanation:\*\*\s*(.+)", response_text, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else "No explanation provided."
        # Return the extracted data using the ArticleOutput model
        return ArticleOutput(
            title=title,
            explanation=explanation,
            interpretation=interpretation,
            confidence=confidence,
            deepfake=None
        )
    except (AttributeError, IndexError) as e:
        raise ValueError(f"Error processing the response: {e}")
