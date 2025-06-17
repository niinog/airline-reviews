import praw
import time
from dotenv import load_dotenv
import os

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def is_airline_post(post, airline_name):
    """Checks if a post is relevant to a specific airline."""
    full_text = (post.title + " " + post.selftext).lower()
    airline_name = airline_name.lower()
    

    if airline_name not in full_text:
        return False

    keywords = [
        "flight", "airline", "plane", "delayed", "cancelled", "boarding",
        "airport", "crew", "baggage", "ticket", "gate", "seat", "service"
    ]
    
    return any(kw in full_text for kw in keywords)


def fetch_airline_posts(airline_name: str, total_limit: int = 1000, search_limit: int = 100):
    """
    Fetches relevant airline posts from Reddit using multiple sort methods.
    """
    all_posts = []
    seen_post_ids = set() # Keep track of post IDs to avoid duplicates within this function

    # Search across different sort methods to maximize results
    sort_methods = ["new", "relevance", "top"]
    
    print(f"Starting fetch for '{airline_name}'. Goal: {total_limit} posts.")

    for sort_method in sort_methods:
        if len(all_posts) >= total_limit:
            break # Stop if we've already reached our goal

        print(f"\n-- Searching with sort='{sort_method}' --")
        last_post_fullname = None

        # This inner loop paginates for the current sort method
        while len(all_posts) < total_limit:
            params = {"after": last_post_fullname} if last_post_fullname else {}
            
            print(f"Collected {len(all_posts)}/{total_limit}. Fetching next batch...")
            
            try:
                search_results = reddit.subreddit("all").search(
                    airline_name,
                    sort=sort_method,
                    limit=search_limit,
                    params=params
                )
            except Exception as e:
                print(f"An error occurred with the API call: {e}")
                time.sleep(5) # Wait before retrying or breaking
                break

            posts_in_batch = 0
            for post in search_results:
                last_post_fullname = post.fullname
                posts_in_batch += 1

                # Avoid processing the same post twice if found via different sort methods
                if post.id in seen_post_ids:
                    continue

                if is_airline_post(post, airline_name):
                    seen_post_ids.add(post.id)
                    post.comments.replace_more(limit=0)
                    top_comments = [
                        comment.body for comment in post.comments.list()[:5]
                    ]

                    all_posts.append({
                        "id": post.id,
                        "title": post.title,
                        "text": post.selftext,
                        "created_utc": post.created_utc,
                        "score": post.score,
                        "url": post.url,
                        "comments": top_comments
                    })

                    if len(all_posts) >= total_limit:
                        break
            
            # If a search yields no results, move to the next sort method
            if posts_in_batch == 0:
                print(f"No more posts found for sort='{sort_method}'.")
                break
            
            time.sleep(1.5) # Be respectful to the API

    print(f"\nFinished fetching. Collected a total of {len(all_posts)} posts.")
    return all_posts


