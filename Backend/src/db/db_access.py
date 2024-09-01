import sqlite3
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

class DatabaseAccess:
    def __init__(self, db_name='database.db'):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def run_in_executor(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, func, *args)

    def _send(self, table_name, data):
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

    async def send(self, table_name, data):
        await self.run_in_executor(self._send, table_name, data)

    def _fetch(self, table_name, conditions=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = f"SELECT * FROM {table_name}"
        if conditions:
            query += f" WHERE {conditions}"

        cursor.execute(query)
        rows = cursor.fetchall()

        conn.close()
        return rows

    async def fetch(self, table_name, conditions=None):
        return await self.run_in_executor(self._fetch, table_name, conditions)


