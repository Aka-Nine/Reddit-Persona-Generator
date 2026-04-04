"""
Configuration settings for Reddit User Persona Generator
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API Configuration
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'PersonaGenerator:v1.0.0 (by /u/yourusername)')

# LLM Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# LLM Model Settings
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'groq')  # 'groq' or 'google'
GROQ_MODEL = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
GOOGLE_MODEL = os.getenv('GOOGLE_MODEL', 'gemini-pro')

# Scraping Configuration
MAX_POSTS = int(os.getenv('MAX_POSTS', '100'))
MAX_COMMENTS = int(os.getenv('MAX_COMMENTS', '200'))
SCRAPING_DELAY = float(os.getenv('SCRAPING_DELAY', '1.0'))

# Analysis Configuration
MIN_TEXT_LENGTH = int(os.getenv('MIN_TEXT_LENGTH', '10'))
MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', '4000'))
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.7'))

# Output Configuration
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
INCLUDE_CITATIONS = os.getenv('INCLUDE_CITATIONS', 'True').lower() == 'true'
CITATION_LIMIT = int(os.getenv('CITATION_LIMIT', '3'))

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'persona_generator.log')

def validate_config():
    """Validate that all required configuration is present."""
    missing = []

    if not REDDIT_CLIENT_ID:
        missing.append("REDDIT_CLIENT_ID")
    if not REDDIT_CLIENT_SECRET:
        missing.append("REDDIT_CLIENT_SECRET")

    if LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
    elif LLM_PROVIDER == "google":
        if not GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER!r} (use 'groq' or 'google')")

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(sorted(set(missing)))}")

    return True