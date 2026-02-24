import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

API_KEY = os.getenv("NEWS_API_KEY")
NEWS_URL = "https://newsapi.org/v2/top-headlines"
# Im Finn made this comment
if not API_KEY:
    raise RuntimeError("NEWS_API_KEY not set")


@app.route("/")
def index():
    return jsonify({"message": "News API running"}), 200


@app.route("/news")
def news():
    try:
        r = requests.get(
            NEWS_URL,
            params={
                "country": "ie",   # Ireland headlines
                "apiKey": API_KEY
            },
            timeout=5
        )

        data = r.json()

        if r.status_code != 200:
            return jsonify({
                "error": "News API error",
                "api_response": data
            }), 502

        articles = [
            {
                "title": a["title"],
                "source": a["source"]["name"],
                "url": a["url"]
            }
            for a in data["articles"]
        ]

        return jsonify({"articles": articles}), 200

    except requests.RequestException as e:
        return jsonify({
            "error": "Failed to contact news service",
            "details": str(e)
        }), 503


if __name__ == "__main__":
    app.run(debug=True)
