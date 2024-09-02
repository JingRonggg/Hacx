#This file contains how the function call should work :)

from db_access import DatabaseAccessAzure

# Initialize the DatabaseAccess class with your Azure SQL Database connection details
db = DatabaseAccessAzure(
    server_name='fakenewsserver.database.windows.net',  
    database_name='FakeNews_DB', 
    username='fakenewsadmin', 
    password='fakenews1!'  
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

