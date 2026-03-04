import os
import requests
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

load_dotenv()

app = Flask(__name__)  # no need to set static_folder

API_KEY = os.getenv("NEWS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

NEWS_URL = "https://newsapi.org/v2/top-headlines"

# Trusted publishers and their NewsAPI source IDs
PUBLISHERS = {
    "BBC News": "bbc-news",
    "New York Times": "the-new-york-times",
    "Washington Post": "the-washington-post",
    "Wall Street Journal": "the-wall-street-journal"
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/headlines")
def get_headlines():
    results = []

    for name, source_id in PUBLISHERS.items():
        r = requests.get(
            NEWS_URL,
            params={
                "sources": source_id,
                "pageSize": 1,
                "apiKey": API_KEY
            },
            timeout=5
        )

        data = r.json()
        headline = "No headline available"

        if data.get("articles"):
            headline = data["articles"][0]["title"]

        results.append({
            "publisher": name,
            "headline": headline
        })

    return jsonify({"headlines": results})


if __name__ == "__main__":
    app.run(debug=True)
