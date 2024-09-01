# setup_db.py

import sqlite3
import os

# Create a database connection
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create input table
cursor.execute('''
CREATE TABLE IF NOT EXISTS input (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Text TEXT NOT NULL,
    Images BLOB
)
''')

# Create processedData table
cursor.execute('''
CREATE TABLE IF NOT EXISTS processedData (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Text TEXT NOT NULL,
    Label BOOLEAN NOT NULL
)
''')

# Create output table
cursor.execute('''
CREATE TABLE IF NOT EXISTS output (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Text TEXT NOT NULL,
    Label BOOLEAN NOT NULL,
    Author TEXT NOT NULL
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Databases and tables created successfully.")
