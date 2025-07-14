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

# Validation Settings
REQUIRED_ENV_VARS = [
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'GROQ_API_KEY'  # or GOOGLE_API_KEY
]

def validate_config():
    """Validate that all required configuration is present"""
    missing_vars = []
    
    for var in REQUIRED_ENV_VARS:
        if var == 'GROQ_API_KEY' and LLM_PROVIDER == 'google':
            continue
        if var == 'GOOGLE_API_KEY' and LLM_PROVIDER == 'groq':
            continue
        if not os.getenv(var):
            missing_vars.append(var)
    
    # Check for LLM provider specific keys
    if LLM_PROVIDER == 'groq' and not GROQ_API_KEY:
        missing_vars.append('GROQ_API_KEY')
    elif LLM_PROVIDER == 'google' and not GOOGLE_API_KEY:
        missing_vars.append('GOOGLE_API_KEY')
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True