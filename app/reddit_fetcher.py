import time
import os
import praw
from dotenv import load_dotenv
from utils.preprocessing import preprocess
from utils.reddit_utils import is_airline_post
from utils.topic_model import get_topic_labels

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

topic_model, topic_labels = get_topic_labels()


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
                time.sleep(5) 
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
    texts = [p["title"] + " " + p["text"] + " " + " ".join(p["comments"]) for p in all_posts]
    cleaned_texts = [preprocess(t) for t in texts]

    topics, _ = topic_model.transform(cleaned_texts)
    topic_labels_mapped = [topic_labels.get(t, "Unknown") for t in topics]

    for post, clean, topic_num, topic_label in zip(all_posts, cleaned_texts, topics, topic_labels_mapped):
        post["cleaned_text"] = clean
        post["topic"] = int(topic_num)
        post["topic_label"] = topic_label

    print("Enrichment complete.")
    return all_posts


