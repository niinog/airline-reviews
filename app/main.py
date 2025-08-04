# app/main.py

from fastapi import FastAPI, Query
from app.reddit_fetcher import fetch_airline_posts
from collections import Counter

app = FastAPI(title="Airline Reddit Post Fetcher")

@app.get("/get_posts")
def get_posts(
    airline: str = Query(..., description="Name of the airline to search for"),
    total_limit: int = Query(1000, description="Total number of posts to fetch")
):
    posts = fetch_airline_posts(airline_name=airline, total_limit=total_limit)
    labels = [post["topic_label"] for post in posts if post.get("topic_label")]
    summary = Counter(labels)
    category_summary = []
    for label, count in summary.items():
        example_post = next((p for p in posts if p.get("topic_label") == label), None)
        example = {
            "url": example_post.get("url"),
            "title": example_post.get("title"),
            "text": example_post.get("text")
        } if example_post else {}

        category_summary.append({
            "topic_label": label,
            "count": count,
            "example": example
        })


    return {
        "airline": airline,
        "post_count": len(posts),
        "category_summary": category_summary,
        "results": posts
    }  
