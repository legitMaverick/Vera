import nltk
nltk.download('punkt_tab')
import requests
import sys
from newspaper import Article, ArticleException

def summarize_article(url):
    """
    Fetches a news article from a given URL, parses it, and generates a summary.

    This function uses the 'newspaper3k' library, which is robust for handling
    various news website structures and extracting the main content reliably.
    
    NOTE: You must install the library first: pip install newspaper3k
    """
    if not url:
        print("Error: URL cannot be empty.")
        return

    try:
        # Define a custom User-Agent to help bypass some anti-bot measures
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        print(f"-> Attempting to download article from: {url}")
        
        # Initialize the Article object with the URL and custom header
        article = Article(url, headers={'User-Agent': user_agent})
        
        # 1. Download the article HTML
        article.download()
        
        # Check if the download was successful
        if not article.html:
             print("Error: Failed to download article content. The URL might be inaccessible or blocking automated access.")
             return

        # 2. Parse the HTML to extract text, title, authors, and publication date
        article.parse()
        
        # 3. Generate the summary (uses an extractive approach built into the library)
        article.nlp()

        print("\n" + "="*50)
        print("✅ SUCCESSFUL EXTRACTION & SUMMARIZATION")
        print("="*50)
        print(f"Title: {article.title}")
        print(f"Authors: {', '.join(article.authors)}")
        # Check if publish_date is available and format it nicely
        publish_date_str = str(article.publish_date).split(' ')[0] if article.publish_date else "N/A"
        print(f"Publish Date: {publish_date_str}")
        print("-" * 50)
        print("Full Article Text Snippet:")
        # Display a snippet of the extracted text for verification
        print(article.text[:500].replace('\n', ' ') + "...")
        print("-" * 50)
        print("GENERATED SUMMARY:")
        print(article.summary)
        print("="*50 + "\n")

    except ArticleException as e:
        print(f"Error: Could not process article (ArticleException). Details: {e}")
        print("Possible causes: URL is invalid, content is inaccessible, or is heavily protected.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Placeholder URL for demonstration if no input is provided
    example_url = "https://www.reuters.com/business/finance/us-treasury-yields-soar-bonds-global-selloff-2024-03-05/" 
    
    # 1. Check if a URL was passed as a command-line argument
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
        print(f"\nNOTE: Using URL provided via command-line argument: {target_url}")
    
    # 2. If no argument is found, prompt the user for input
    else:
        # --- PROMPT FOR USER INPUT ---
        print("-" * 50)
        user_input = input("Please enter the URL of the news article you wish to summarize (or press Enter to use the example URL): ")
        print("-" * 50)
        
        if user_input.strip():
            target_url = user_input.strip()
            print(f"Using provided URL: {target_url}")
        else:
            # Fall back to a different, more reliable example URL
            print(f"No URL entered. Falling back to example URL: {example_url}")
            target_url = example_url

    # 3. Call the summarization function
    summarize_article(target_url)