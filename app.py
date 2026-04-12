import os
import time
import logging
import requests
import psycopg2
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Basic logging setup (shows time + message in terminal)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Get API key and database URL from environment
API_KEY = os.getenv("NEWS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# NewsAPI endpoint
NEWS_URL = "https://newsapi.org/v2/top-headlines"

# List of publishers we want headlines from
PUBLISHERS = {
    "BBC News": "bbc-news",
    "Washington Post": "the-washington-post",
    "Wall Street Journal": "the-wall-street-journal"
}


# Create a database connection
def get_conn():
    return psycopg2.connect(DATABASE_URL)


# Fetch latest headline from each publisher
def fetch_current_headlines():
    results = []

    # Loop through each publisher
    for name, source_id in PUBLISHERS.items():
        try:
            # Call NewsAPI
            r = requests.get(
                NEWS_URL,
                params={
                    "sources": source_id,
                    "pageSize": 1,   # only get top article
                    "apiKey": API_KEY
                },
                timeout=5
            )

            data = r.json()

            # Default values if something goes wrong
            headline = "No headline found"
            url = "#"

            # If request worked and articles exist
            if r.status_code == 200 and data.get("articles"):
                article = data["articles"][0]
                headline = article.get("title", "No headline found")
                url = article.get("url", "#")

            logging.info(f"{name}: headline retrieved")

        except Exception as e:
            # If API call fails
            logging.error(f"Error retrieving {name}: {e}")
            headline = "Error retrieving headline"
            url = "#"

        # Add result to list
        results.append({
            "publisher": name,
            "headline": headline,
            "url": url
        })

    return results


# Home page (loads index.html)
@app.route("/")
def index():
    return render_template("index.html")


# Health check endpoint (basic check if app is running)
@app.route("/health")
def health():
    logging.info("Health check requested")
    return jsonify({
        "status": "ok",
        "service": "NewsFlash",
        "timestamp": int(time.time())
    })


# Get live headlines from API
@app.route("/headlines")
def get_headlines():
    logging.info("Fetching live headlines")
    results = fetch_current_headlines()
    return jsonify({"headlines": results})


# Fetch headlines and save them to database
@app.route("/save-headlines")
def save_headlines():
    logging.info("Saving headlines to Supabase")
    results = fetch_current_headlines()

    try:
        # Open database connection
        with get_conn() as conn:
            with conn.cursor() as cur:
                for item in results:
                    # Insert into table (ignore duplicates using URL)
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


# Get saved headlines from database
@app.route("/saved-headlines")
def saved_headlines():
    logging.info("Reading saved headlines from Supabase")

    try:
        # Query database
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

        # Convert DB rows into JSON format
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


# Run the app (used locally and in Docker)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)