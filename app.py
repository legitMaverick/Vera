import sys
import random
import time
import requests 
from typing import Optional, Tuple, Dict, Any
from flask import Flask, render_template, request, jsonify 
from newspaper import Article, ArticleException
from datetime import datetime

# --- NEW IMPORTS for Sentiment Analysis ---
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
# ----------------------------------------

# NOTE: You MUST have a Business.py file in the same directory containing the get_news function.
# Example call: news_articles = get_news(category='world news', country='us', pagesize=15)
from Business import get_news 

# --- A. False News Checker Class (Statistical Model) ---

class FalseNewsChecker:
    """
    A simulated statistical machine learning model for checking false news.
    (Included here for integration convenience)
    """

    def __init__(self):
        self.sensational_keywords: Dict[str, float] = {
            "shocking": 0.25, "exclusive": 0.15, "must see": 0.20,
            "disaster": 0.10, "scam": 0.30, "fake news": -0.5, 
            "truth": 0.05, "exposed": 0.22, "viral": 0.18,
        }
        self.MISINFO_THRESHOLD: float = 0.55
        self.MANIPULATION_THRESHOLD: float = 0.70

    def _analyze_text_for_bias(self, url: str, content: str = "") -> float:
        """ Simulates statistical text classification. """
        text = (url + " " + content).lower()
        bias_score = 0.0
        for keyword, weight in self.sensational_keywords.items():
            count = text.count(keyword)
            bias_score += count * weight
        if "blogspot" in url or "wordpress" in url or url.endswith(".co"):
            bias_score += 0.3
        if any(bad_pattern in url for bad_pattern in ["hoax", "conspiracy", "rumor"]):
            bias_score += 0.4
        final_score = min(bias_score / 2.5, 1.0)
        return final_score

    def _analyze_image_for_manipulation(self, file_size_kb: int, noise_factor: float) -> float:
        """ Simulates statistical image forensic analysis. """
        manipulation_score = 0.0
        manipulation_score += noise_factor * 0.45
        if file_size_kb < 100 and noise_factor > 0.5:
            manipulation_score += 0.35
        if random.random() < noise_factor: 
            manipulation_score += 0.20
        return min(manipulation_score, 1.0)

    def check(self, url: str, image_features: Optional[Tuple[int, float]] = None, content: str = "") -> Dict[str, Any]:
        """ Runs both text and image analysis. """
        text_score = self._analyze_text_for_bias(url, content)
        image_score = 0.0
        
        if image_features:
            file_size_kb, noise_factor = image_features
            image_score = self._analyze_image_for_manipulation(file_size_kb, noise_factor)

        # Final Score Calculation (60% Text, 40% Image/Text for fairness if image is missing)
        weight_image = 0.4 if image_features else 0.0
        final_misinfo_score = (text_score * 0.6) + (image_score * weight_image) + (text_score * (0.4 - weight_image))
        
        verdict = "VERIFIED (Low Risk)"
        
        if final_misinfo_score > self.MANIPULATION_THRESHOLD:
            verdict = "HIGH MISINFORMATION RISK 🚨"
        elif final_misinfo_score > self.MISINFO_THRESHOLD:
            verdict = "CAUTION ADVISED (High Bias/Uncertainty) ⚠️"
            
        return {
            "verdict": verdict,
            "score": f"{final_misinfo_score:.2f}",
            "text_score": f"{text_score:.2f}",
            "image_score": f"{image_score:.2f}"
        }

# --- B. Summarization Function ---

def summarize_article(url):
    """
    Fetches a news article from a given URL, parses it, and generates a summary.
    Returns a tuple: (data_dict, status_code)
    """
    if not url:
        return {"error": "URL cannot be empty."}, 400

    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        article = Article(url, headers={'User-Agent': user_agent})
        
        article.download()
        if not article.html:
            return {"error": "Failed to download article content. The URL might be inaccessible or blocking automated access."}, 400

        article.parse()
        article.nlp() # Generate the summary and keywords

        return {
            "title": article.title or "No Title Extracted",
            "authors": ', '.join(article.authors) or "N/A",
            "summary": article.summary or "Could not generate summary.",
            "date": str(article.publish_date).split(' ')[0] if article.publish_date else "N/A"
        }, 200

    except ArticleException as e:
        return {"error": f"Could not process article (ArticleException). Details: {e}"}, 400
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}, 500


# --- C. Flask App Initialization and Configuration ---

app = Flask(__name__)
checker = FalseNewsChecker() # Initialize the False News Checker model
CATEGORIES = [
    'Home', 'Business', 'Entertainment', 'Health', 
    'Lifestyle', 'Science', 'Sports', 'World News'
]

# -------------------------------------------------------------
## 1. SENTIMENT MODEL SETUP (TRAINED ONCE AT STARTUP)

# Sample Labeled Dataset 
SENTIMENT_DATA = {
    'review': [
        "This product is absolutely amazing and exceeded all my expectations.",
        "The service was terrible and I will never return to this restaurant.",
        "It was an okay experience, nothing special or bad.",
        "I love the speed and efficiency of the new software update.",
        "The movie was a huge disappointment and a waste of time.",
        "Everything worked perfectly, highly recommend it to everyone.",
        "Neutral feeling about the purchase, it does the job.",
        "The price is too high for such a poor quality item.",
        "The economic situation is dire and many jobs are at risk.",
        "Global leaders signed a landmark climate agreement, a monumental step forward."
    ],
    # 1: Positive, 0: Neutral, -1: Negative
    'sentiment': [1, -1, 0, 1, -1, 1, 0, -1, -1, 1]
}
sentiment_df = pd.DataFrame(SENTIMENT_DATA)

# Define input features (X_s) and target labels (y_s)
X_s = sentiment_df['review']
y_s = sentiment_df['sentiment']

# Initialize and Fit TF-IDF Vectorizer
sentiment_vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(1, 2))
X_s_tfidf = sentiment_vectorizer.fit_transform(X_s)

# Model Training
sentiment_model = MultinomialNB()
sentiment_model.fit(X_s_tfidf, y_s)

def get_sentiment_prediction(text: str) -> Dict[str, str]:
    """Predicts sentiment for new text using the trained model and returns result map."""
    if not text or not text.strip():
        return {'sentiment': "N/A", 'emoji': "❓", 'color': 'text-gray-500'}

    # Transform the text using the fitted vectorizer
    text_tfidf = sentiment_vectorizer.transform([text])
    
    # Make the prediction
    prediction = sentiment_model.predict(text_tfidf)[0]
    
    # Map the numerical label back to a descriptive sentiment
    if prediction == 1:
        return {'sentiment': "Positive", 'emoji': "😄", 'color': 'text-green-500'}
    elif prediction == -1:
        return {'sentiment': "Negative", 'emoji': "😠", 'color': 'text-red-500'}
    else:
        return {'sentiment': "Neutral", 'emoji': "😐", 'color': 'text-yellow-500'}

# -------------------------------------------------------------

# --- D. API Routes (Updated with /api/sentiment) ---

@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    """API endpoint to receive a URL and return a summarized article (using newspaper3k)."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "Missing URL in request."}), 400

    summary_data, status_code = summarize_article(url)
    return jsonify(summary_data), status_code

@app.route('/check', methods=['POST'])
def run_false_news_check():
    """API endpoint to receive URL, Content, and simulated image features for fact-checking."""
    data = request.get_json()
    
    url = data.get('url', 'URL Not Provided')
    content = data.get('content', '')
    
    file_size_kb = data.get('file_size_kb')
    noise_factor = data.get('noise_factor')

    image_features = None
    
    try:
        # Check if both simulated image features are provided and valid
        if file_size_kb is not None and noise_factor is not None:
            image_features = (int(file_size_kb), float(noise_factor))
    except (ValueError, TypeError):
        pass 

    result = checker.check(
        url=url,
        content=content,
        image_features=image_features
    )
    
    return jsonify(result)

@app.route('/api/sentiment', methods=['POST'])
def api_sentiment_analysis():
    """NEW API endpoint to receive text and return sentiment analysis results."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    input_text = data.get('text', '')
    
    # Run the sentiment prediction
    result = get_sentiment_prediction(input_text)
    
    # Return the results as JSON
    return jsonify(result)


# --- E. Frontend Routing Logic (Jinja Template Rendering) ---

def render_category_page(category_name, category_slug):
    """Helper function to fetch news and render the template for a category."""
    # Ensure the slug is correctly handled by your Business.py (e.g., 'world news' should be 'general' for NewsAPI)
    api_slug = category_slug if category_slug not in ['World News', 'Home'] else 'general'
    
    news_articles = get_news(category=api_slug, country='us', pagesize=15)
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return render_template(
        'index.html', 
        articles=news_articles, 
        current_category=category_name, 
        categories=CATEGORIES,
        current_date=current_date
    )

@app.route('/')
@app.route('/home')
def home():
    """Home page route."""
    return render_category_page('Home', 'general')

@app.route('/category/business')
def business_page():
    """Business page route."""
    return render_category_page('Business', 'business')

@app.route('/category/health')
def health_page():
    return render_category_page('Health', 'health')

@app.route('/category/entertainment')
def entertainment_page():
    return render_category_page('Entertainment', 'entertainment')

@app.route('/category/lifestyle')
def lifestyle_page():
    # Mapping 'Lifestyle' to 'science' or 'health' as a placeholder slug
    return render_category_page('Lifestyle', 'health') 

@app.route('/category/science')
def science_page():
    return render_category_page('Science', 'science')

@app.route('/category/sports')
def sports_page():
    return render_category_page('Sports', 'sports')

@app.route('/category/world-news')
def world_news_page():
    # Mapping 'World News' to 'general' as a placeholder slug
    return render_category_page('World News', 'general')


@app.route('/category/<category_name>')
def category_placeholder(category_name):
    """Placeholder route for non-explicitly defined categories."""
    display_name = category_name.replace('-', ' ').title()
    current_date = datetime.now().strftime("%B %d, %Y")
    
    placeholder_article = [{
        'title': f'Feature Not Available: {display_name} News',
        'url': '#',
        'source': 'Veritas Chronicle System',
        'description': f'The **{display_name}** category is not yet enabled. This is a placeholder page.',
        'image_url': None,
        'category': 'placeholder'
    }]
    
    return render_template(
        'index.html',
        articles=placeholder_article,
        current_category=display_name,
        categories=CATEGORIES,
        current_date=current_date
    )

    
if __name__ == '__main__':
    print("Running Veritas Chronicle App...")
    app.run(debug=True)