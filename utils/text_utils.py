
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from textstat import flesch_reading_ease
from collections import Counter

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove Reddit-specific formatting
    text = re.sub(r'/u/\w+', '', text)  # Remove user mentions
    text = re.sub(r'/r/\w+', '', text)  # Remove subreddit mentions
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)  # Remove markdown links
    text = re.sub(r'&gt;.*', '', text)  # Remove quotes
    
    # Clean whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def extract_keywords(text: str, top_n: int = 10) -> list:
    """Extract top keywords from text"""
    if not text:
        return []
    
    # Tokenize and clean
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    
    # Filter words
    keywords = [word for word in words if word.isalpha() and word not in stop_words and len(word) > 2]
    
    # Count and return top keywords
    word_freq = Counter(keywords)
    return [word for word, count in word_freq.most_common(top_n)]

def calculate_readability(text: str) -> float:
    """Calculate Flesch Reading Ease score"""
    if not text:
        return 0.0
    
    try:
        return flesch_reading_ease(text)
    except:
        return 0.0