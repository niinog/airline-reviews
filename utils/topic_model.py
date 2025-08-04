from bertopic import BERTopic

topic_model = BERTopic.load("models/bertopic_model")

topic_labels = {
    -1: "General",
     0: "Travel Booking",
     1: "Compensation & Claims",
     2: "Luggage & Boarding",
     3: "Backpack & Personal Items",
     4: "Flight Safety & Accidents",
     5: "Politics & International Affairs"
}

def get_topic_labels():
    return topic_model, topic_labels
