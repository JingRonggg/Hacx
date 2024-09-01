#This file contains how the function call should work :)

from db.db_access import DatabaseAccess

db = DatabaseAccess(db_name='database.db')

# Example of inserting data
db.send("processedData", ("Example text", True))

# Example of extracting data
data = db.extract("processedData", "Label = 1")
print(data)

# Example of deleting data
db.delete("processedData", "Text = 'Example text'")
