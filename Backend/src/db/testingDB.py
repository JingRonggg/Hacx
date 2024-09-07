# This file contains how the function call should work :)

from db_access import DatabaseAccessAzure
import os
from dotenv import load_dotenv


load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
SERVER_NAME = os.getenv("SERVER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
SERVER_USERNAME = os.getenv("SERVER_USERNAME")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")

# Initialize the DatabaseAccess class with your Azure SQL Database connection details
db = DatabaseAccessAzure(
    server_name=SERVER_NAME,  
    database_name=DATABASE_NAME, 
    username=SERVER_USERNAME, 
    password=SERVER_PASSWORD  
)

# # Example of inserting data into the input_data table
# db.send("input_data", ("Sample Title", "Sample Main Text", "John", "Sample Description"))
# db.send("input_data", ("Sample Title", "Sample Main Text1", "John", "Sample Description"))

# # # Example of extracting data from the input_data table
data = db.extract("input_data", "author = 'John'")
print(data)

# # Example of deleting data from the input_data table
db.delete("input_data", "maintext = 'Sample Main Text1'")


data = db.extract("input_data", "author = 'John'")
print(data)

