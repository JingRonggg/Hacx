import pyodbc

class DatabaseAccessAzure:
    def __init__(self, server_name, database_name, username, password):
        self.conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server_name};"
            f"DATABASE={database_name};"
            f"UID={username};"
            f"PWD={password};"
            "Connection Timeout=60;"
        )

    # Send function to insert data into Azure SQL Database
    def send(self, table_name, data):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()

        if table_name == "input_data":
            cursor.execute("INSERT INTO dbo.input_data (title, maintext, author, description, url) VALUES (?, ?, ?, ?, ?)", data)
        elif table_name == "pre_processed_data":
            cursor.execute("INSERT INTO dbo.pre_processed_data (statement, label) VALUES (?, ?)", data)
        elif table_name == "output_data":
            cursor.execute("INSERT INTO dbo.output_data (statement, label) VALUES (?, ?)", data)
        else:
            raise ValueError("Table name not recognized.")

        conn.commit()
        cursor.close()
        conn.close()

    # Extract function to retrieve data from Azure SQL Database
    def extract(self, table_name, conditions=None): 
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()

        query = f"SELECT * FROM dbo.{table_name}"
        
        if conditions:
            conditions = conditions.replace('author', 'CAST(author AS VARCHAR(MAX))')
            conditions = conditions.replace('maintext', 'CAST(maintext AS VARCHAR(MAX))')
            conditions = conditions.replace('description', 'CAST(description AS VARCHAR(MAX))')
            conditions = conditions.replace('url', 'CAST(url AS VARCHAR(MAX))')
            query += f" WHERE {conditions}"

        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return rows

    # Delete function to remove data from Azure SQL Database
    def delete(self, table_name, conditions=None):
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()

        query = f"DELETE FROM dbo.{table_name}"
        
        if conditions:
            conditions = conditions.replace('author', 'CAST(author AS VARCHAR(MAX))')
            conditions = conditions.replace('maintext', 'CAST(maintext AS VARCHAR(MAX))')
            conditions = conditions.replace('description', 'CAST(description AS VARCHAR(MAX))')
            conditions = conditions.replace('url', 'CAST(url AS VARCHAR(MAX))')  
            query += f" WHERE {conditions}"

        cursor.execute(query)
        conn.commit()

        cursor.close()
        conn.close()