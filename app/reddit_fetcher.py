import praw
import time
from dotenv import load_dotenv
import os
import re
from bertopic import BERTopic
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('wordnet')

topic_model = BERTopic.load("../bertopic_model")

topic_labels = {
    -1: "General",
     0: "Travel Booking",
     1: "Compensation & Claims",
     2: "Luggage & Boarding",
     3: "Backpack & Personal Items",
     4: "Flight Safety & Accidents",
     5: "Politics & International Affairs"
}

# Preprocessing function
lemmatizer = WordNetLemmatizer()
extra_stopwords = set(["la","die","nu","cu","der","ca","pentru","und","das","sa","im","ive","dont","cant","wont","didnt"])
stop_words = set(stopwords.words('english')).union(extra_stopwords)
airline_names = ["easyjet", "ryanair", "turkish", "wizz", "air", "airways", "british","lufthansa","klm","delta","emirates","qatar","etihad","united","american","alitalia","airfrance","aeroflot"]

def preprocess(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and word not in airline_names and len(word) > 2]
    return ' '.join(tokens)

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


