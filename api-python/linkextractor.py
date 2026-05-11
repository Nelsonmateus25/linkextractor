#!/usr/bin/env python3

from flask import Flask, Response
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import urljoin
import redis
import json
import os

app = Flask(__name__)

USE_CACHE = os.environ.get("USE_CACHE", "true").lower() == "true"
redis_client = None

if USE_CACHE:
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    try:
        redis_client = redis.StrictRedis.from_url(redis_url, socket_connect_timeout=2)
        redis_client.ping()
        print(f"[Python API] Redis conectado: {redis_url}", flush=True)
    except Exception as e:
        print(f"[Python API] Redis indisponível: {e}. Cache desativado.", flush=True)
        redis_client = None
        USE_CACHE = False

if not USE_CACHE:
    print("[Python API] Iniciando SEM cache.", flush=True)


def extract_links(url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; LinkExtractor/1.0)"}
    req = Request(url, headers=headers)
    response = urlopen(req, timeout=10)
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href", "").strip()
        text = a_tag.get_text(strip=True) or "[IMG]"
        try:
            full_url = urljoin(url, href)
            links.append({"text": text, "href": full_url})
        except Exception:
            pass
    return links


@app.route("/")
def index():
    return "Usage: http://<hostname>[:<prt>]/api/<url>"


@app.route("/api/<path:url>")
def api(url):
    if USE_CACHE and redis_client:
        cached = redis_client.get(url)
        if cached:
            return Response(cached, status=200, mimetype="application/json")

    links = extract_links(url)
    json_links = json.dumps(links, indent=2, ensure_ascii=False)

    if USE_CACHE and redis_client:
        redis_client.set(url, json_links)

    return Response(json_links, status=200, mimetype="application/json")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
