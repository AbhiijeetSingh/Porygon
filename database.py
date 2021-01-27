# Create a database instance, and connect to it.
from databases import Database
import asyncio


async def insert_data(info):
    query = "INSERT INTO HighScores(name, score) VALUES (:name, :score)"
    values = [
        {"id": id, "title": title, "score": 92},
    ]
    await database.execute_many(query=query, values=values)


async def main():
    database = Database('sqlite:///files_info.db')
    await database.connect()

    # Create a table.
    query = """CREATE TABLE HighScores (id INTEGER PRIMARY KEY, title VARCHAR(100),  INTEGER)"""
    await database.execute(query=query)

    # Run a database query.
    query = "SELECT * FROM HighScores"
    rows = await database.fetch_all(query=query)
    print('High Scores:', rows)

asyncio.run(main())
