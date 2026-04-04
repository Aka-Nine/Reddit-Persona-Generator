"""
Configuration settings for Reddit User Persona Generator
"""

import logging
import os
import warnings
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

_logger = logging.getLogger(__name__)

# Groq retires model IDs periodically; map old env values to a supported default.
_DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
_DEPRECATED_GROQ_MODELS = {
    "mixtral-8x7b-32768": _DEFAULT_GROQ_MODEL,
    "mixtral-8x7b-instruct": _DEFAULT_GROQ_MODEL,
    "llama3-70b-8192": _DEFAULT_GROQ_MODEL,
    "llama3-8b-8192": "llama-3.1-8b-instant",
    "llama2-70b-4096": _DEFAULT_GROQ_MODEL,
}


def _resolve_groq_model(raw: Optional[str]) -> str:
    if not raw or not str(raw).strip():
        return _DEFAULT_GROQ_MODEL
    key = str(raw).strip().lower()
    if key in _DEPRECATED_GROQ_MODELS:
        replacement = _DEPRECATED_GROQ_MODELS[key]
        warnings.warn(
            f"GROQ_MODEL '{raw.strip()}' is no longer supported by Groq; using '{replacement}' instead. "
            "Update your .env or hosting variables. See https://console.groq.com/docs/models",
            UserWarning,
            stacklevel=2,
        )
        _logger.warning(
            "Remapping deprecated GROQ_MODEL %r -> %r", raw.strip(), replacement
        )
        return replacement
    return str(raw).strip()

# Reddit API Configuration
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'PersonaGenerator:v1.0.0 (by /u/yourusername)')

# LLM Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# LLM Model Settings
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'groq')  # 'groq' or 'google'
GROQ_MODEL = _resolve_groq_model(os.getenv("GROQ_MODEL"))
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