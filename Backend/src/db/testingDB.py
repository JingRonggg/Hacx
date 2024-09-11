from db_access import DatabaseAccessAzure
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Configuration
SERVER_NAME = os.getenv("SERVER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
SERVER_USERNAME = os.getenv("SERVER_USERNAME")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")


# Check if environment variables are loaded correctly
if not all([SERVER_NAME, DATABASE_NAME, SERVER_USERNAME, SERVER_PASSWORD]):
    print("Error: One or more environment variables are missing.")
    exit(1)

# Initialize the DatabaseAccess class with your Azure SQL Database connection details
db = DatabaseAccessAzure(
    server_name=SERVER_NAME,
    database_name=DATABASE_NAME,
    username=SERVER_USERNAME,
    password=SERVER_PASSWORD
)


def createinput(tablename, data):
    try:
        '''print("Inserting data into input_data table...")
        for url in urls: 
        article_data = fetch_article(url)
        title = article_data["title"]
        maintext = article_data["text"]
        author = article_data["authors"]
        date = article_data["publish_date"]'''
        print("Inserting data into input_data table...")
        db.send(tablename, data)
        print("Done inserting")
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")


# # Example of inserting data into the input_data table
'''try:
     print("Inserting data into input_data table...")
     db.send("input_data", ("Sample Title", "Sample Main Text", "John", "Sample Description", "http://example1.com"))
     db.send("input_data", ("Sample Title 2", "Sample Main Text 2", "John", "Sample Description 2", "http://example2.com"))
     print("Data inserted successfully.")
except Exception as e:
     print(f"An error occurred while inserting data: {e}")'''

# # Example of extracting data from the input_data table
# try:
#     print("Extracting data from input_data table where author is 'John'...")
#     data = db.extract("input_data", "author = 'John'")
#     print("Extracted data:")
#     for row in data:
#         print(row)
# except Exception as e:
#     print(f"An error occurred while extracting data: {e}")

# Example of deleting data from the input_data table
def deleterecord():
    try:
        print("Deleting data from input_data table where maintext is 'Sample Main Text 2'...")
        db.delete("input_data", "maintext = 'Sample Main Text'")
        print("Data deleted successfully.")
    except Exception as e:
        print(f"An error occurred while deleting data: {e}")

# Extract data again to verify deletion
def readtable():
    try:
        print("Extracting data again to verify deletion...")
        data = db.extract("input_data", "author = 'John'")
        print("Data after deletion:")
        for row in data:
            print(row)
    except Exception as e:
        print(f"An error occurred while extracting data after deletion: {e}")
