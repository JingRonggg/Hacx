#This file contains how the function call should work :)

from db.db_access import DatabaseAccess

# Example usage
# remember await needs to be used within an async function
async def main():
    db = DatabaseAccess()

    # Send data to the input table
    await db.send("input", ("Sample Text", "image.png"))

    # Fetch data from the input table
    rows = await db.fetch("input")
    print(rows)

# To run the example
# asyncio.run(main())