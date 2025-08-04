import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
extra_stopwords = set(["la","die","nu","cu","der","ca","pentru","und","das","sa","im","ive","dont","cant","wont","didnt"])
stop_words = set(stopwords.words('english')).union(extra_stopwords)
airline_names = [
    "easyjet", "ryanair", "turkish", "wizz", "air", "airways", "british",
    "lufthansa", "klm", "delta", "emirates", "qatar", "etihad",
    "united", "american", "alitalia", "airfrance", "aeroflot"
]

def preprocess(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and word not in airline_names and len(word) > 2
    ]
    return ' '.join(tokens)
