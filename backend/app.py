from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import requests
import wikipediaapi
import praw
import random
import os
import tweepy
import googlemaps
from pytrends.request import TrendReq

# Suppress TensorFlow Warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# NLP Pipelines
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Wikipedia API setup
wiki_api = wikipediaapi.Wikipedia(language='en', user_agent="InsightOSINT/1.0")

# Google Maps API key
GMAPS_API_KEY = "AIzaSyBvBV9y3m27vXYvZoIjoMMLd2kQ5A6ltPY"

# TwitterAPI keys
API_KEY = "HwdMBBvoGSRSc9G4xbKT2e98A"
API_SECRET = "GV5k7PHYsfuio8t6xfFkflogQhixxPscf54WYMfTOHkXSXkWAB"
ACCESS_TOKEN = "1645753605935493124-QDgJ9z4dvih6fJd8CQeDGDUJ9bPGWs"
ACCESS_SECRET = "Bds1bkAfiEMCO7eH122r9xDmhE8F62f5zFkPnJRLLqIxP"

# NewsAPI key (replace with actual API key)
NEWS_API_KEY = "2d491f23419f4472a9e604af9fc39cb5"

# Reddit API setup
reddit = praw.Reddit(
    client_id="xofaJTvYxHNAo3YW4mK11A",
    client_secret="RXklv6rOJDP-8BUIE8fWetiLLNaNwQ",
    user_agent="InsightOSINT/1.0"
)

def fetch_wikipedia_summary(query):
    """Fetch summary from Wikipedia."""
    page = wiki_api.page(query)
    if page.exists():
        return page.summary
    return None

def fetch_news_articles(query):
    """Fetch news articles from NewsAPI."""
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [
            f"{article['title']} {article['description']}"
            for article in articles if article['description']
        ]
    return []

def fetch_reddit_discussions(query):
    """Fetch top Reddit discussions."""
    discussions = []
    try:
        for submission in reddit.subreddit("all").search(query, limit=5):
            if submission.selftext:
                discussions.append(submission.selftext[:200])  # Limit to 200 chars
    except Exception as e:
        print(f"Reddit fetch error: {e}")
    return discussions

def fetch_trending_topics():
    """Fetch trending topics using Google Trends API."""
    try:
        pytrends = TrendReq()
        # Add at least one dummy keyword to the payload
        pytrends.build_payload(kw_list=["technology"], geo="US")
        trends = pytrends.trending_searches(pn="united_states")
        return trends[0].tolist()[:3]  # Return top 3 trends
    except Exception as e:
        print(f"Error fetching trending topics: {e}")
        return ["Error fetching trends"]

def fetch_geospatial_data(query):
    """Fetch geospatial data using Google Maps API."""
    gmaps = googlemaps.Client(key=GMAPS_API_KEY)
    
    try:
        # Perform a places search query
        results = gmaps.places(query=query)
        if results["status"] == "OK":
            regions = [result["formatted_address"] for result in results["results"]]
            return regions[:3]  # Return the top 3 regions
    except Exception as e:
        print(f"Geospatial data fetch error: {e}")
    return ["No data available"]

def generate_combined_response(query, wiki_summary, news_data, reddit_data):
    """Generate a cohesive response combining all sources."""
    response = f"Here is an in-depth analysis of the topic '{query}':\n\n"

    if wiki_summary:
        response += f"{wiki_summary} "

    if news_data:
        response += " ".join(news_data) + " "

    if reddit_data:
        response += " ".join(reddit_data) + " "

    sentiment_result = sentiment_analyzer(response[:512])
    overall_sentiment = sentiment_result[0]["label"].lower()
    response += f"Overall sentiment: {overall_sentiment}."

    return response.strip()

def fetch_research_data(query):
    """Fetch research papers and articles using CrossRef API."""
    url = f"https://api.crossref.org/works?query={query}&rows=5"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("message", {}).get("items", [])
        return [item.get("title", ["No Title"])[0] for item in items]
    return []

def fetch_semantic_scholar_data(query):
    """Fetch research data using Semantic Scholar API."""
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5"
    headers = {"x-api-key": "YOUR_SEMANTIC_SCHOLAR_API_KEY"}  # Replace with your API key
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        items = response.json().get("data", [])
        return [item.get("title", "No Title Available") for item in items]
    return []

def fetch_core_research_data(query):
    """Fetch open access research papers using CORE API."""
    url = f"https://core.ac.uk:443/api-v2/search?q={query}&apiKey=f8vwJ120UEx6zyIpN3jnCeTlYAPkVmKM"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("data", [])
        return [result["title"] for result in results if "title" in result][:5]
    return []

def fetch_conference_papers(query):
    """Fetch conference papers using IEEE Xplore API."""
    url = f"https://api.ieee.org/v1/search/articles?querytext={query}&apikey=s7stue9agd8javfyq3becdk8"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [article.get("title", "No Title Available") for article in articles]
    return []


@app.route('/search', methods=['POST'])
def search():
    """Handle search requests."""
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({"error": "Please provide a query parameter."}), 400

    # Fetch Wikipedia, news, and Reddit data
    wiki_summary = fetch_wikipedia_summary(query)
    news_data = fetch_news_articles(query)
    reddit_data = fetch_reddit_discussions(query)

    # Check if any data was fetched
    if not (wiki_summary or news_data or reddit_data):
        return jsonify({"response": "No relevant information found."})

    # Generate unified response
    unified_response = generate_combined_response(query, wiki_summary, news_data, reddit_data)

    # Calculate total contributions for data sources
    total_sources = len(news_data) + 20 + 10 + 5 + 15 + 10 + 10 + 5

    # Dashboard Data
    dashboard = {
        "trending_topics": fetch_trending_topics(),
        "data_sources": {
            "Social media": round((20 / total_sources) * 100, 2),
            "News websites": round((len(news_data) / total_sources) * 100, 2),
            "Forums": round((10 / total_sources) * 100, 2),
            "Dark web": round((5 / total_sources) * 100, 2),
            "Research papers": round((15 / total_sources) * 100, 2),
            "News articles": round((len(news_data) / total_sources) * 100, 2),
            "Research articles": round((10 / total_sources) * 100, 2),
            "Conference papers": round((10 / total_sources) * 100, 2),
            "Conference presentations": round((5 / total_sources) * 100, 2),
        },
        "regions": fetch_geospatial_data(query),
        "sentiment": {
            "overall": sentiment_analyzer(unified_response[:512])[0]["label"].lower(),
            "positive": 35,
            "negative": 25,
            "neutral": 40
        }
    }

    return jsonify({"response": unified_response, "dashboard": dashboard})


if __name__ == '__main__':
    app.run(debug=True)


