import sqlite3
import os

class DatabaseAccess:
    def __init__(self, db_name='database.db'):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)

    # send function as previously defined
    def send(self, table_name, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if table_name == "input":
            cursor.execute("INSERT INTO input (Text, Images) VALUES (?, ?)", data)
        elif table_name == "processedData":
            cursor.execute("INSERT INTO processedData (Text, Label) VALUES (?, ?)", data)
        elif table_name == "output":
            cursor.execute("INSERT INTO output (Text, Label, Author) VALUES (?, ?, ?)", data)
        else:
            raise ValueError("Table name not recognized.")

        conn.commit()
        conn.close()

    # extract function as previously defined
    def extract(self, table_name, conditions=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = f"SELECT * FROM {table_name}"
        if conditions:
            query += f" WHERE {conditions}"

        cursor.execute(query)
        rows = cursor.fetchall()

        conn.close()
        return rows

    # New delete function
    def delete(self, table_name, conditions=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = f"DELETE FROM {table_name}"
        if conditions:
            query += f" WHERE {conditions}"

        cursor.execute(query)
        conn.commit()
        conn.close()

# Example usage
if __name__ == "__main__":
    db = DatabaseAccess(db_name='database.db')

    # Example of extracting data
    data = db.extract("processedData")
    print(data)