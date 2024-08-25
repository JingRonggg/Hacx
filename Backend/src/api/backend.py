import fastapi

app = fastapi.FastAPI()

@app.get("/")
async def health() -> dict:
    """
    Root API endpoint to check the health of the service.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"messages": "Hello Hacx!"}
