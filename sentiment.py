import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import sys
import os 
import re 
from typing import Dict, Any

# -------------------------------------------------------------
# --- 1. DATA LOADING AND PREPROCESSING (Using all-data.csv) ---
# -------------------------------------------------------------

FINNA_FILE = 'all-data.csv' # Using the uploaded filename

# Load the dataset
try:
    # This specific loading method handles the common structure of the FINN-A dataset: 
    # [label,"text"] without a header.
    df = pd.read_csv(
        FINNA_FILE, 
        header=None, 
        encoding='latin-1', 
        sep='\",', 
        engine='python', 
        names=['sentiment', 'review']
    )
    # Clean up the text and sentiment columns
    df['review'] = df['review'].str.strip('"')
    df['sentiment'] = df['sentiment'].str.strip().str.lower()
except Exception as e:
    # Fallback for a different file structure, if the above fails
    print(f"Error loading data with specified format: {e}. Attempting simple CSV load.")
    try:
        df = pd.read_csv(FINNA_FILE, header=None, encoding='latin-1', names=['sentiment', 'review'])
    except Exception as e_fallback:
        print(f"Failed to load data: {e_fallback}")
        sys.exit(1)


# Map string labels to numerical labels: 
# 'positive' -> 1, 'negative' -> -1, 'neutral' -> 0
sentiment_map = {'positive': 1, 'negative': -1, 'neutral': 0}
df['sentiment'] = df['sentiment'].map(sentiment_map)

# Remove any rows where mapping failed or text is missing
df.dropna(subset=['review', 'sentiment'], inplace=True)
df = df[df['review'].str.strip().astype(bool)] # Remove empty reviews

print(f"Successfully loaded and pre-processed {len(df)} financial news samples.")


# -------------------------------------------------------------
# --- 2. FEATURE EXTRACTION & MODEL TRAINING ---
# -------------------------------------------------------------

X = df['review']
y = df['sentiment']

# Initialize and Fit TF-IDF Vectorizer
# Training on the entire, large corpus now provides a robust vocabulary.
tfidf_vectorizer = TfidfVectorizer(
    stop_words='english', 
    lowercase=True, 
    ngram_range=(1, 2)
)

X_tfidf = tfidf_vectorizer.fit_transform(X)

# 3. Model Training (Multinomial Naive Bayes)
model = MultinomialNB()
model.fit(X_tfidf, y)

print("Model training complete.")

# --- End of Training Pipeline ---
# ---------------------------------

def predict_sentiment(text: str) -> str:
    """Predicts sentiment for new text using the trained model and returns a formatted string."""
    if not text.strip():
        return "N/A (Empty Input)"
        
    # Preprocess text (must match vectorizer setup)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower()) # Simple cleaning

    # Convert the new text into TF-IDF features using the fitted vectorizer
    text_tfidf = tfidf_vectorizer.transform([text])
    
    # Make the prediction
    prediction = model.predict(text_tfidf)[0]
    
    # Map the numerical label back to a descriptive sentiment
    if prediction == 1:
        return f"Positive (1) 😄"
    elif prediction == -1:
        return f"Negative (-1) 😠"
    else:
        return f"Neutral (0) 😐"

def run_sentiment_analyzer():
    """Main loop to take user input and display sentiment."""
    print("✨ Sentiment Analysis Tool (Trained on FINN-A Financial News) ✨")
    print("-" * 50)
    print("Enter the text you want to analyze (e.g., a news headline).")
    print("Type 'quit' or 'exit' to stop the program.")
    print("-" * 50)
    
    # Example to confirm the fix for the sports headline:
    test_headline = "India beat South Africa: ICC Women’s World Cup final 2025"
    print(f"[Test] Headline: {test_headline}")
    print(f"[Test Result] Sentiment: {predict_sentiment(test_headline)}\n")
    print("-" * 50)

    while True:
        try:
            # Taking input from the user
            user_input = input("Analyze > ")
            
            if user_input.lower() in ['quit', 'exit']:
                print("\nAnalyzer shut down. Goodbye! 👋")
                break
            
            if not user_input.strip():
                print("Please enter some text to analyze.")
                continue

            # Get and display the prediction
            sentiment_result = predict_sentiment(user_input)
            print(f"\n[Result] Sentiment: {sentiment_result}\n")

        except EOFError:
            # Handle Ctrl+D or end of file
            print("\nAnalyzer shut down. Goodbye! 👋")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

# Execute the main function
if __name__ == "__main__":
    run_sentiment_analyzer()