import os
import json
import pandas as pd
import datetime

DATA_FOLDER = "data"
OUTPUT_FILE = "all_airlines_clean.csv"

def flatten_comments(comments):
    return " || ".join(comments) if isinstance(comments, list) else ""

def assign_category(text):
    text = text.lower()
    if any(word in text for word in ["delay", "delayed", "late", "cancelled"]):
        return "Flight Delay"
    elif any(word in text for word in ["baggage", "luggage", "lost bag"]):
        return "Baggage"
    elif any(word in text for word in ["crew", "staff", "attendant"]):
        return "Crew"
    elif any(word in text for word in ["seat", "legroom", "assigned seat"]):
        return "Seating"
    elif any(word in text for word in ["check-in", "boarding", "gate"]):
        return "Check-in & Boarding"
    elif any(word in text for word in ["food", "meal", "drink"]):
        return "In-flight Service"
    elif any(word in text for word in ["app", "website", "login", "tech"]):
        return "Technical/App"
    elif any(word in text for word in ["price", "cost", "refund", "overcharge", "fee", "paid", "charged"]):
        return "Pricing / Fees"
    elif any(word in text for word in ["customer service", "support", "agent", "call center", "rude", "help"]):
        return "Customer Service"
    elif any(word in text for word in ["miles", "points", "loyalty", "frequent flyer", "membership", "rewards", "bilt", "partner airline", "transfer", "1:1"]):
        return "Loyalty Program"
    elif any(word in text for word in ["notification", "informed", "email", "message", "texted"]):
        return "Communication"
    elif any(word in text for word in ["safety", "emergency", "turbulence", "oxygen", "seatbelt", "pilot"]):
        return "Safety Concern"
    elif any(word in text for word in ["carbon offset", "sustainable", "emissions", "eco", "environment"]):
        return "Sustainability"
    elif any(word in text for word in ["fragrance", "amenities", "entertainment", "blanket", "comfort", "snack"]):
        return "Onboard Experience"
    elif any(word in text for word in ["flight path", "route", "flying direction", "detour"]):
        return "Flight Path / Routing"
    elif any(word in text for word in ["airport", "announcement", "partnership", "expansion", "news", "policy", "update", "press release", "surge", "security agency"]):
        return "Airline News"
    elif any(word in text for word in ["antonov", "an-124", "flyover", "spotted", "jet engine noise", "engine sound"]):
        return "Plane Spotting"
    else:
        return "Other"

# Load existing CSV (if exists) and track existing IDs
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_csv(OUTPUT_FILE)
    existing_ids = set(df_existing["id"].dropna())
else:
    df_existing = pd.DataFrame()
    existing_ids = set()

# Collect new data
all_rows = []

for filename in os.listdir(DATA_FOLDER):
    if not filename.endswith("_reddit.json"):
        continue

    airline = filename.replace("_reddit.json", "").replace("_", " ")
    filepath = os.path.join(DATA_FOLDER, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        posts = json.load(f)

    for post in posts:
        post_id = post.get("id", "")
        if post_id in existing_ids:
            continue  # skip if already exists

        title = post.get("title", "")
        text = post.get("text", "")
        comments = flatten_comments(post.get("comments", []))
        combined_text = f"{title} {text} {comments}".strip()
        category = assign_category(combined_text)

        created_utc = post.get("created_utc")
        if created_utc is not None:
            # Convert Unix timestamp to datetime object
            dt_object = datetime.datetime.fromtimestamp(created_utc, tz=datetime.timezone.utc)
            formatted_created_utc = dt_object.strftime("%Y/%m")  # → e.g., '2024/02'
 
        else:
            formatted_created_utc = None 

        all_rows.append({
            "airline": airline,
            "id": post_id,
            "title": title,
            "text": text,
            "comments": comments,
            "combined_text": combined_text,
            "category": category,
            "score": post.get("score", 0),
            "url": post.get("url", ""),
            "created_utc": formatted_created_utc
        })

# Append new data if any
if all_rows:
    df_new = pd.DataFrame(all_rows)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f" Appended {len(df_new)} new posts. Total now: {len(df_combined)}")
else:
    print(f" No new posts to append.")
