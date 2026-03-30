import os
import time
import logging
import requests
import psycopg2
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

API_KEY = os.getenv("NEWS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

NEWS_URL = "https://newsapi.org/v2/top-headlines"

PUBLISHERS = {
    "BBC News": "bbc-news",
    "New York Times": "the-new-york-times",
    "Washington Post": "the-washington-post",
    "Wall Street Journal": "the-wall-street-journal"
}


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def fetch_current_headlines():
    results = []

    for name, source_id in PUBLISHERS.items():
        try:
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

            logging.info(f"{name}: headline retrieved")

        except Exception as e:
            logging.error(f"Error retrieving {name}: {e}")
            headline = "Error retrieving headline"
            url = "#"

        results.append({
            "publisher": name,
            "headline": headline,
            "url": url
        })

    return results


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    logging.info("Health check requested")
    return jsonify({
        "status": "ok",
        "service": "NewsFlash",
        "timestamp": int(time.time())
    })


@app.route("/headlines")
def get_headlines():
    logging.info("Fetching live headlines")
    results = fetch_current_headlines()
    return jsonify({"headlines": results})


@app.route("/save-headlines")
def save_headlines():
    logging.info("Saving headlines to Supabase")
    results = fetch_current_headlines()

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                for item in results:
                    cur.execute(
                        """
                        insert into news (publisher, headline, url)
                        values (%s, %s, %s)
                        on conflict (url) do nothing
                        """,
                        (item["publisher"], item["headline"], item["url"])
                    )

        return jsonify({
            "message": "Headlines saved to database",
            "count": len(results)
        })

    except Exception as e:
        logging.error(f"Database save error: {e}")
        return jsonify({
            "error": "Failed to save headlines",
            "details": str(e)
        }), 500


@app.route("/saved-headlines")
def saved_headlines():
    logging.info("Reading saved headlines from Supabase")

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select publisher, headline, url
                    from news
                    order by id desc
                    limit 20
                    """
                )
                rows = cur.fetchall()

        results = [
            {
                "publisher": row[0],
                "headline": row[1],
                "url": row[2]
            }
            for row in rows
        ]

        return jsonify({"headlines": results})

    except Exception as e:
        logging.error(f"Database read error: {e}")
        return jsonify({
            "error": "Failed to read headlines",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)