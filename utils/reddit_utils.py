def is_airline_post(post, airline_name):
    full_text = (post.title + " " + post.selftext).lower()
    airline_name = airline_name.lower()
    if airline_name not in full_text:
        return False

    keywords = [
        "flight", "airline", "plane", "delayed", "cancelled", "boarding",
        "airport", "crew", "baggage", "ticket", "gate", "seat", "service"
    ]
    return any(kw in full_text for kw in keywords)
