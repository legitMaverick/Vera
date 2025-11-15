# news_fetcher.py

import os
from newsapi import NewsApiClient

# --- Configuration ---
# IMPORTANT: Use your actual API Key
api_key = '29175e24500f416cbff3008d6065aef2' 

# Initialize the News API client once
try:
    newsapi = NewsApiClient(api_key=api_key)
except ValueError as e:
    print(f"Error initializing NewsApiClient: {e}") 
    newsapi = None

# --- Unified Fetch News Function ---
def get_news(category, country='us', pagesize=10):
    """
    Fetches top headlines for a given category and RETURNS a list of article dictionaries,
    formatted for the Jinja template.
    """
    if not newsapi:
        # Return structured error data if the API client failed to initialize
        return [{'title': 'API Client Failed to Initialize', 'source': 'System Error', 'url': '#', 'category': 'Error'}]

    # NewsAPI uses 'general' for both World News and Lifestyle
    api_category = 'general'
    if category in ['business', 'entertainment', 'health', 'science', 'sports', 'technology']:
        api_category = category
    # Note: If category is 'world news' or 'lifestyle', api_category remains 'general'.
    
    try:
        top_headlines = newsapi.get_top_headlines(
            category=api_category,
            language='en',
            country=country,
            page_size=pagesize
        )

        articles_list = []
        for article in top_headlines.get('articles', []):
            # Structure the data exactly as the Jinja template expects
            articles_list.append({
                'title': article.get('title', 'No Title'),
                'url': article.get('url', '#'),
                'source': article.get('source', {}).get('name', 'Unknown Source'),
                'description': article.get('description', article.get('content', '')),
                'image_url': article.get('urlToImage'),
                # Use the lowercase category name for color mapping in HTML
                'category': category.lower().replace(' ', '-') 
            })
        
        # CRUCIAL CHANGE: Return the list of articles
        return articles_list
        
    except Exception as e:
        print(f"An error occurred while fetching news for {category}: {e}")
        # Return structured error data for display
        return [{'title': f'Error fetching {category} news', 'source': 'API Error', 'url': '#', 'category': 'Error'}]

# The '__main__' block is removed, as Flask will import and call this function.