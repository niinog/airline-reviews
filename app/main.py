# app/main.py

from fastapi import FastAPI, Query
from app.reddit_fetcher import fetch_airline_posts

app = FastAPI(title="Airline Reddit Post Fetcher")

@app.get("/get_posts")
def get_posts(
    airline: str = Query(..., description="Name of the airline to search for"),
    total_limit: int = Query(1000, description="Total number of posts to fetch")
):
    posts = fetch_airline_posts(airline_name=airline, total_limit=total_limit)
    return {
        "airline": airline,
        "post_count": len(posts),
        "results": posts
    }
