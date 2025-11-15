import os
from newsapi import NewsApiClient
from datetime import datetime, timedelta

# --- Configuration ---
# IMPORTANT: Replace 'YOUR_API_KEY' with your actual NewsAPI key.
# Get one for free from https://newsapi.org/
api_key = '29175e24500f416cbff3008d6065aef2' 

# Initialize the News API client
try:
    newsapi = NewsApiClient(api_key=api_key)
except ValueError as e:
    print(f"Error initializing NewsApiClient: {e}")
    print("Please ensure your API key is correctly set.")
    exit()

# --- Fetch News ---
def get_health_news(country='us', category='health', pagesize=10):
    """Fetches top health headlines from NewsAPI."""
    
    print(f"--- Top {pagesize} Health Headlines ({country.upper()}) ---")
    
    try:
        # Get top headlines for the specified category and country
        top_headlines = newsapi.get_top_headlines(
            category=category,
            language='en',
            country=country,
            page_size=pagesize
        )

        articles = top_headlines.get('articles', [])
        
        if not articles:
            print("No articles found.")
            return

        for i, article in enumerate(articles):
            title = article.get('title', 'No Title')
            source = article.get('source', {}).get('name', 'Unknown Source')
            url = article.get('url', 'No URL')

            print(f"\n{i+1}. **{title}**")
            print(f"   Source: {source}")
            print(f"   Link: {url}")
            
    except Exception as e:
        print(f"An error occurred while fetching news: {e}")

# --- Run the script ---
if __name__ == "__main__":
    # The 'category' is set to 'health' by default in the function definition.
    # You can change 'us' to 'in', 'gb', etc., to get health news from other regions.
    get_health_news(country='us', pagesize=5)