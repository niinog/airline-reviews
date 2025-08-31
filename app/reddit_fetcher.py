# reddit_fetcher.py
import os
import praw
from dotenv import load_dotenv
from typing import List, Dict
from diskcache import Cache

from utils.preprocessing import preprocess
from utils.reddit_utils import is_airline_post
from utils.topic_model import get_topic_labels

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)
reddit.read_only = True

# persistent on-disk cache (works across app restarts if disk is persistent)
cache = Cache("./cache_dir")
CACHE_TOPIC_TTL = 24 * 3600  # 24h

_topic_model = None
_topic_labels = None

def _ensure_topic_model():
    global _topic_model, _topic_labels
    if _topic_model is None:
        _topic_model, _topic_labels = get_topic_labels()

def _assign_topics_inplace(posts: List[Dict]):
    """Assign topics with per-post caching to avoid recomputing."""
    _ensure_topic_model()

    # Which posts still need a topic?
    to_compute = []
    cleaned_texts = []
    idxs = []

    for i, p in enumerate(posts):
        pid = p["id"]
        cached = cache.get(f"topic:{pid}")
        if cached is not None:
            topic_num = int(cached)
            p["topic"] = topic_num
            p["topic_label"] = _topic_labels.get(topic_num, "Unknown")
            # optional: also cache cleaned_text if you need it later
        else:
            text = f'{p.get("title","")} {p.get("text","")}'
            cleaned = preprocess(text)
            to_compute.append(pid)
            cleaned_texts.append(cleaned)
            idxs.append(i)

    if not to_compute:
        return

    topics, _ = _topic_model.transform(cleaned_texts)
    for pid, i, topic_num in zip(to_compute, idxs, topics):
        topic_num = int(topic_num)
        posts[i]["topic"] = topic_num
        posts[i]["topic_label"] = _topic_labels.get(topic_num, "Unknown")
        cache.set(f"topic:{pid}", topic_num, expire=CACHE_TOPIC_TTL)

def fetch_airline_posts(
    airline_name: str,
    total_limit: int = 200,
    sort: str = "relevance",         # "new", "top", "relevance"
    time_filter: str = "year",       # "hour","day","week","month","year","all"
    include_comments: bool = False,  # fetch comments only on demand
    with_topics: bool = False,       # compute topics for returned posts
) -> List[Dict]:
    """
    Fast path:
    - one search call with a large limit (PRAW paginates internally)
    - no comments by default (huge speedup)
    - optional topic labeling with per-post caching
    """
    query = f'title:"{airline_name}" OR {airline_name}'

    selected: List[Dict] = []
    seen = set()

    # ask for more than you need because you'll filter with is_airline_post
    raw_limit = min(total_limit * 3, 1000)

    for post in reddit.subreddit("all").search(
        query, sort=sort, time_filter=time_filter, limit=raw_limit
    ):
        if post.id in seen:
            continue
        if not is_airline_post(post, airline_name):
            continue

        seen.add(post.id)

        top_comments = []
        if include_comments:
            # WARNING: this is slow; only use when the user opens a post
            post.comments.replace_more(limit=0)
            top_comments = [c.body for c in post.comments.list()[:5]]

        selected.append({
            "id": post.id,
            "title": post.title,
            "text": post.selftext,
            "created_utc": post.created_utc,
            "score": post.score,
            "url": post.url,
            "num_comments": getattr(post, "num_comments", None),
            "comments": top_comments,  # usually empty
        })

        if len(selected) >= total_limit:
            break

    if with_topics and selected:
        _assign_topics_inplace(selected)

    return selected
