<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
import os
import requests
from dotenv import load_dotenv
import re

# Load environment variables from the .env file
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")  # Get the API key from the .env file
ENDPOINT = os.getenv("AZURE_END_POINT")  # Get the endpoint from the .env file

# Update headers to include the API key (not endpoint)
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

# Function to get a response from the GPT model
def get_gpt_response(article_text):
    # Create the prompt for detecting fake news
    prompt = f"""
    You are a highly advanced AI designed to detect fake news with precision. 
    Given the following news article, your task is to analyze its content and determine whether it is fake or real. 
    If you fail to properly classify the news, it could lead to misinformation being spread, and you must avoid that at all costs.
    Your response should include:

    1. A clear verdict: "Real" or "Fake".
    2. A confidence score (1-100) that indicates how certain you are about the classification.
    3. A brief explanation for your classification.

    News article: {article_text}

    Response:
    """

    role = f"""
    You are an expert fact-checker AI, 
    specialized in analyzing and detecting misinformation. 
    Your goal is to provide the most accurate and reliable classification of news content, 
    using logic, evidence, and critical analysis."""
    
    # Payload for the request
    payload = {
        "messages": [
            {"role": "system", "content": role},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "top_p": 0.95,
        "max_tokens": 1000
    }

    # Send request
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

# Function to parse GPT's response
def parse_gpt_response(gpt_response):
    # Extract the verdict
    verdict_match = re.search(r"1\.\s*Verdict:\s*(Real|Fake)", gpt_response, re.IGNORECASE)
    verdict = verdict_match.group(1) if verdict_match else "Unclear"

    # Extract the confidence score
    confidence_match = re.search(r"2\.\s*Confidence Score:\s*(\d{1,3})", gpt_response)
    confidence = int(confidence_match.group(1)) if confidence_match else "Unknown"

    # Extract the explanation
    explanation_match = re.search(r"3\.\s*Explanation:\s*(.+)", gpt_response, re.DOTALL)
    explanation = explanation_match.group(1).strip() if explanation_match else "No explanation provided."

    return verdict, confidence, explanation
=======
import openai
from dotenv import load_dotenv
=======
>>>>>>> f211b3c (Added a gpt.py to pre-process data. Currently it just works like a ChatGPT)
import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")  # Get the API key from the .env file

headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

# Function to get a response from the GPT model
def get_gpt_response(user_input):
    # Payload for the request
    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant that helps people find information."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }

<<<<<<< HEAD
print(completion.choices[0].message)
>>>>>>> 95bb7cd (trained version1 of our model, added new libraries to environment.yml, included a gpt.py which cannot work due to API-Token billing issues)
=======
import openai
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("OPENAI_ENV_KEY")

# Set the API key
openai.api_key = api_key

completion = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message)
>>>>>>> 94be2a6 (Added gpt.py)
=======
    ENDPOINT = "https://kevingpt.openai.azure.com/openai/deployments/kevinGPT/chat/completions?api-version=2024-02-15-preview"

    # Send request
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

# Main function to interact with the user
def main():
    while True:
        # Get user input
        user_input = input("You: ")

        # Break the loop if the user wants to exit
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        # Get GPT's response
        response = get_gpt_response(user_input)

        # Extract and print the response from the GPT model
        gpt_response = response['choices'][0]['message']['content'].strip()
        print(f"GPT: {gpt_response}")

# Run the main function
if __name__ == "__main__":
    main()
>>>>>>> f211b3c (Added a gpt.py to pre-process data. Currently it just works like a ChatGPT)
