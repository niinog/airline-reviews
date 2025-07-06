# collect_all.py

from app.reddit_fetcher import fetch_airline_posts
import json
import os
import time 


print("Running NEW alldata.py version with 4 airlines only!")
def save_to_json(data, airline_name):
    os.makedirs("data", exist_ok=True)
    filename = f"data/{airline_name.replace(' ', '_')}_reddit.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f" Saved {len(data)} posts to {filename}")


# all_airlines = [
#     "Ryanair", "Wizz Air", "Turkish Airlines", "Qatar Airways",
#     "Emirates", "Lufthansa", "Delta", "United Airlines", "EasyJet", "Pegasus Airlines"
# ]
airlines = [
    "Ryanair", "Wizz Air", "Turkish Airlines",  "EasyJet"
]
# airlines = [
#     airline for airline in all_airlines
#     if not os.path.exists(f"data/{airline.replace(' ', '_')}_reddit.json")
# ]
for airline in airlines:
    print(f"\n Collecting posts for: {airline}")
    new_posts = fetch_airline_posts(airline_name=airline, total_limit=300)

    # Build path to the existing JSON file
    filename = f"data/{airline.replace(' ', '_')}_reddit.json"

    # Load old posts if file exists
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing_posts = json.load(f)
    else:
        existing_posts = []

    # Avoid duplicates using post ID
    existing_ids = {post["id"] for post in existing_posts}
    unique_new_posts = [post for post in new_posts if post["id"] not in existing_ids]

    # Combine old + new
    combined = existing_posts + unique_new_posts
    save_to_json(combined, airline)

    print(f" Added {len(unique_new_posts)} new posts (Total: {len(combined)})")
    time.sleep(5)

