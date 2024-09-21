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
        elif table_name == "output_data":
            cursor.execute("""
                INSERT INTO dbo.output_data 
                (title, explanation, interpretation, confidence, deepfake, sentiment, sentiment_explanation, disinformation, disinformation_explanation, target_Audience, url, added_time) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                data)
        elif table_name == "manual_data":
            cursor.execute("""
                INSERT INTO dbo.manual_data 
                (title, explanation, interpretation, confidence, deepfake, sentiment, sentiment_explanation, disinformation, disinformation_explanation, target_Audience) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                , data)
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
        
        if table_name == "input_data":
            if conditions:
                conditions = conditions.replace('author', 'CAST(author AS VARCHAR(MAX))')
                conditions = conditions.replace('maintext', 'CAST(maintext AS VARCHAR(MAX))')
                conditions = conditions.replace('description', 'CAST(description AS VARCHAR(MAX))')
                conditions = conditions.replace('url', 'CAST(url AS VARCHAR(MAX))')
                query += f" WHERE {conditions}"
        elif table_name == "output_data":
            if conditions:
                conditions = conditions.replace('interpretation_for_fakenews', 'CAST(interpretation_for_fakenews AS VARCHAR(MAX))')
                conditions = conditions.replace('explanation_for_fakenews', 'CAST(explanation_for_fakenews AS VARCHAR(MAX))')
                conditions = conditions.replace('confidence_for_fakenews', 'CAST(confidence_for_fakenews AS VARCHAR(MAX))')
                conditions = conditions.replace('deepfake', 'CAST(deepfake AS VARCHAR(MAX))')
                conditions = conditions.replace('sentiment', 'CAST(sentiment AS VARCHAR(MAX))')
                conditions = conditions.replace('explanation_for_sentiment', 'CAST(explanation_for_sentiment AS VARCHAR(MAX))')
                conditions = conditions.replace('disinformation', 'CAST(disinformation AS VARCHAR(MAX))')
                conditions = conditions.replace('explanation_for_disinformation', 'CAST(explanation_for_disinformation AS VARCHAR(MAX))')
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
        
        if table_name == "input_data":
            if conditions:
                conditions = conditions.replace('author', 'CAST(author AS VARCHAR(MAX))')
                conditions = conditions.replace('maintext', 'CAST(maintext AS VARCHAR(MAX))')
                conditions = conditions.replace('description', 'CAST(description AS VARCHAR(MAX))')
                conditions = conditions.replace('url', 'CAST(url AS VARCHAR(MAX))')  
                query += f" WHERE {conditions}"
        elif table_name == "output_data":
            if conditions:
                conditions = conditions.replace('interpretation_for_fakenews', 'CAST(interpretation_for_fakenews AS VARCHAR(MAX))')
                conditions = conditions.replace('explanation_for_fakenews', 'CAST(explanation_for_fakenews AS VARCHAR(MAX))')
                conditions = conditions.replace('confidence_for_fakenews', 'CAST(confidence_for_fakenews AS VARCHAR(MAX))')
                conditions = conditions.replace('deepfake', 'CAST(deepfake AS VARCHAR(MAX))')
                conditions = conditions.replace('sentiment', 'CAST(sentiment AS VARCHAR(MAX))')
                conditions = conditions.replace('explanation_for_sentiment', 'CAST(explanation_for_sentiment AS VARCHAR(MAX))')
                conditions = conditions.replace('disinformation', 'CAST(disinformation AS VARCHAR(MAX))')
                conditions = conditions.replace('explanation_for_disinformation', 'CAST(explanation_for_disinformation AS VARCHAR(MAX))')
                query += f" WHERE {conditions}"

        cursor.execute(query)
        conn.commit()

        cursor.close()
        conn.close()

    # Query function to execute a custom SQL query 
    def query(self, sql_query, params=None):
        """Executes a SQL query and returns the results."""
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()

        # Execute the query with optional parameters
        if params:
            cursor.execute(sql_query, params)
        else:
            cursor.execute(sql_query)

        rows = cursor.fetchall()  # Fetch all rows from the result set

        cursor.close()
        conn.close()
        return rows