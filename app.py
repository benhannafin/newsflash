import os
import requests
import psycopg2
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)  # no need to set static_folder

API_KEY = os.getenv("NEWS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

NEWS_URL = "https://newsapi.org/v2/top-headlines"

def get_conn():
    return psycopg2.connect(DATABASE_URL)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sync-news")
def sync_news():
    r = requests.get(
        NEWS_URL,
        params={"country": "ie", "apiKey": API_KEY},
        timeout=5
    )
    data = r.json()

    articles = [
        (a["title"], a["source"]["name"], a["url"])
        for a in data.get("articles", [])
        if a.get("title") and a.get("url") and a.get("source", {}).get("name")
    ]

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                insert into news (title, source, url)
                values (%s, %s, %s)
                on conflict (url) do nothing
                """,
                articles
            )

    return jsonify({"stored": len(articles)})


@app.route("/stored-news")
def stored_news():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select title, source, url from news order by id desc limit 50")
            rows = cur.fetchall()

    return jsonify({"articles": [{"title": t, "source": s, "url": u} for (t, s, u) in rows]})


@app.route("/sources")
def sources():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select distinct source from news order by source")
            rows = cur.fetchall()

    return jsonify({"sources": [r[0] for r in rows]})