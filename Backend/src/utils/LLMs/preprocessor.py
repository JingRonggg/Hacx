import os
import requests
from dotenv import load_dotenv
from db.db_access import DatabaseAccessAzure

load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
SERVER_NAME = os.getenv("SERVER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
SERVER_USERNAME = os.getenv("SERVER_USERNAME")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")

headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

# Initialize Database Access
db = DatabaseAccessAzure(
    server_name = SERVER_NAME,  
    database_name = DATABASE_NAME,  
    username = SERVER_USERNAME,  
    password = SERVER_PASSWORD
)

# Function to get a response from the GPT model
def get_gpt_response(user_input):
    modified_input = f"{user_input}\n\nCarefully classify the statements in the above text into True or False. Consider common scientific knowledge, geography, and historical facts when making your classification. When listing True or False Statements, omit the numberings. When the sentence has ended, just move on to the next line."

    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant that helps people find information."},
            {"role": "user", "content": modified_input}
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }

    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

# Function to process the GPT response and classify statements
def classify_statements(gpt_response):
    classification_dict = {"True": [], "False": []}
    lines = gpt_response.splitlines()

    for line in lines:
        if line.startswith("True:"):
            statement = line.replace("True: ", "").strip()
            classification_dict["True"].append(statement)
        elif line.startswith("False:"):
            statement = line.replace("False: ", "").strip()
            classification_dict["False"].append(statement)

    return classification_dict

# Main function to process input data from the database and store processed data
def main():
    input_data = db.extract("input_data")

    for record in input_data:
        maintext = record[2]  # Only use the maintext field

        response = get_gpt_response(maintext)
        gpt_response = response['choices'][0]['message']['content'].strip()
        classified_dict = classify_statements(gpt_response)

        # Store classified statements into the pre_processed_data table
        for truth_value, statements in classified_dict.items():
            label = 1 if truth_value == "True" else 0
            for statement in statements:
                db.send("pre_processed_data", (statement, label))
