# news_fetcher.py

import os
from newsapi import NewsApiClient
# Note: datetime/timedelta are not needed for this basic fetch, but kept for context

# --- Configuration ---
# IMPORTANT: Use your actual API key
api_key = '29175e24500f416cbff3008d6065aef2' 

# Initialize the News API client once
try:
    newsapi = NewsApiClient(api_key=api_key)
except ValueError as e:
    # In a Flask app, logging this error is better than exiting
    print(f"Error initializing NewsApiClient: {e}") 
    newsapi = None

# --- Fetch News Function (Modified to RETURN data) ---
def get_news_by_category(category, country='us', pagesize=10):
    """
    Fetches top headlines for a given category and returns a list of article dictionaries.
    
    NOTE: We generalize the function name since you will use it for all categories.
    """
    if not newsapi:
        return [{'title': 'API Client Failed to Initialize', 'source': 'System Error', 'url': '#'}]

    try:
        top_headlines = newsapi.get_top_headlines(
            category=category,
            language='en',
            country=country,
            page_size=pagesize
        )

        articles_list = []
        for article in top_headlines.get('articles', []):
            # Structure the data exactly as needed by the Jinja template
            articles_list.append({
                'title': article.get('title', 'No Title'),
                'url': article.get('url', '#'),
                'source': article.get('source', {}).get('name', 'Unknown Source'),
                'description': article.get('description', ''),
                'image_url': article.get('urlToImage'),
                'category': category # Add the category back for color mapping in HTML
            })
        
        # This is the crucial change: returning the data instead of printing
        return articles_list
        
    except Exception as e:
        print(f"An error occurred while fetching news: {e}")
        return [{'title': f'Error fetching {category} news', 'source': 'API Error', 'url': '#'}]

# We remove the "if __name__ == '__main__':" block here.