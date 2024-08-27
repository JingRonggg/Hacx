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