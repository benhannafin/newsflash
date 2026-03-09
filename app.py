import os
import requests
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("NEWS_API_KEY")

NEWS_URL = "https://newsapi.org/v2/top-headlines"

# Trusted publishers
PUBLISHERS = {
    "BBC News": "bbc-news",
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

        headline = "No headline found"
        url = "#"

        if r.status_code == 200 and data.get("articles"):
            article = data["articles"][0]
            headline = article.get("title", "No headline found")
            url = article.get("url", "#")

        results.append({
            "publisher": name,
            "headline": headline,
            "url": url
        })

    return jsonify({"headlines": results})


if __name__ == "__main__":
    app.run(debug=True)
