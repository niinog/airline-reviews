# app/main.py

from fastapi import FastAPI, Query
from app.reddit_fetcher import fetch_airline_posts
from collections import Counter
from diskcache import Cache

cache = Cache("./cache_dir")
app = FastAPI(title="Airline Reddit Post Fetcher")
@cache.memoize(expire=3600)
def get_cached_posts_full(airline: str, total_limit: int):
    # Pass the total_limit from the function argument
    return fetch_airline_posts(airline_name=airline, total_limit=total_limit, with_topics=True)


@app.get("/get_posts")
def get_posts(
    airline: str = Query(..., description="Name of the airline to search for"),
    total_limit: int = Query(1000, description="Total number of posts to fetch")
):
    all_posts = get_cached_posts_full(airline, total_limit)
    posts = all_posts[:total_limit]
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
