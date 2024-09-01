# db_access.py

import sqlite3
import os

class DatabaseAccess:
    def __init__(self, db_name='database.db'):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)

    # send(table_name, data): Sends data to the specified table. 
    # Data should be provided as a tuple matching the table's column order.
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

    # extract(table_name, conditions): Extracts data from the specified table. 
    # Optional conditions parameter can be used to filter results (e.g., Text = 'some text').
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
