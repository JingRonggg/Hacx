from db.db_access import DatabaseAccess
import pandas as pd
from sklearn.model_selection import train_test_split

db = DatabaseAccess(db_name='database.db')

# Example inputs
input1 = ("Breaking news: The stock market hits an all-time high.", True)
input2 = ("Aliens have landed in New York City, claims anonymous source.", False)
input3 = ("Scientists discover water on Mars, increasing hopes for life.", True)

# Insert the inputs into the processedData table
#db.send("processedData", input1)
#b.send("processedData", input2)
#db.send("processedData", input3)


# Load data from the processedData table using db_access
def load_data_from_db():
    db = DatabaseAccess(db_name='database.db')
    data = db.extract("processedData")  # Extract data from processedData table
    df = pd.DataFrame(data, columns=['id', 'Text', 'Label'])  # Assuming the data has Text and Label columns
    return df

# Split the data into train, test, and validation sets
def split_data(data):
    train_data, temp_data = train_test_split(data, test_size=0.25, random_state=42, stratify=data['Label'])
    test_data, valid_data = train_test_split(temp_data, test_size=0.6, random_state=42, stratify=temp_data['Label'])
    return train_data, test_data, valid_data

data = load_data_from_db()
print(data)