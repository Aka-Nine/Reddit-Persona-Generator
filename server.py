# server.py — production-friendly Flask app for Reddit persona generation
import logging
import os
import sys

# Ensure imports resolve (CLI adds src/; keep same layout for gunicorn)
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
_src = os.path.join(_ROOT, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import nltk
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from config import OUTPUT_DIR, validate_config

# Web API: default off — avoids writing to ephemeral disk on Railway; clients use sessionStorage.
PERSONA_WRITE_TO_DISK = os.getenv("PERSONA_WRITE_TO_DISK", "false").lower() in (
    "1",
    "true",
    "yes",
)
from src.citation_manager import CitationManager
from src.data_processor import DataProcessor
from src.output_generator import OutputGenerator
from src.persona_analyzer import PersonaAnalyzer
from src.reddit_scraper import RedditScraper
from utils.reddit_url import validate_reddit_url

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

DEBUG = os.getenv("FLASK_DEBUG", "").lower() in ("1", "true", "yes")

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["JSON_SORT_KEYS"] = False
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_REQUEST_BYTES", "65536"))


def _ensure_nltk():
    """Download NLTK data once per process (Docker / cold start)."""
    bundles = [
        ("punkt", "tokenizers/punkt"),
        ("punkt_tab", "tokenizers/punkt_tab"),
        ("stopwords", "corpora/stopwords"),
    ]
    for name, path in bundles:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(name, quiet=True)
            except Exception as ex:
                logger.warning("NLTK resource %s: %s", name, ex)


_ensure_nltk()

_cors = os.getenv("CORS_ORIGINS", "*").strip()
if _cors == "*":
    CORS(app)
else:
    CORS(app, origins=[o.strip() for o in _cors.split(",") if o.strip()])


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/health")
@app.route("/healthz")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/analyze", methods=["POST"])
def analyze():
    if not request.is_json:
        return jsonify({"success": False, "error": "Expected Content-Type: application/json"}), 415

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"success": False, "error": "Invalid JSON body"}), 400

    profile_url = (payload.get("profile_url") or "").strip()
    if not profile_url:
        return jsonify({"success": False, "error": "Missing profile_url"}), 400

    try:
        validate_config()
        username = validate_reddit_url(profile_url)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    logger.info("Processing request for: %s", profile_url)

    try:
        scraper = RedditScraper()
        processor = DataProcessor()
        analyzer = PersonaAnalyzer()
        citation_manager = CitationManager()
        output_generator = OutputGenerator()

        logger.info("Starting Reddit data scraping...")
        user_data = scraper.scrape_user_data(username)
        logger.info(
            "Scraped %s posts and %s comments",
            len(user_data["posts"]),
            len(user_data["comments"]),
        )

        logger.info("Processing scraped data...")
        processed_data = processor.process_user_data(user_data)

        logger.info("Analyzing user persona...")
        persona_data = analyzer.analyze_persona(processed_data)

        logger.info("Generating citations...")
        citations = citation_manager.generate_citations(persona_data, user_data)

        if PERSONA_WRITE_TO_DISK:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            output_path = os.path.join(OUTPUT_DIR, f"{username}_persona.txt")
            output_generator.generate_persona_file(
                persona_data, citations, output_path, username
            )
            with open(output_path, "r", encoding="utf-8") as f:
                persona_content = f.read()
            saved_path = output_path
        else:
            persona_content = output_generator.render_persona_text(
                persona_data, citations, username
            )
            saved_path = None
            logger.info("Skipping persona file write (PERSONA_WRITE_TO_DISK=false); client should persist.")

        return jsonify(
            {
                "success": True,
                "message": "Persona generated successfully",
                "username": username,
                "file_path": saved_path,
                "persona_content": persona_content,
                "persisted_to_disk": PERSONA_WRITE_TO_DISK,
            }
        )

    except ValueError as e:
        logger.warning("Validation error: %s", e)
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.exception("Error generating persona")
        msg = str(e).lower()
        if "model_decommissioned" in msg or "decommissioned" in msg:
            err = (
                "Groq model is no longer supported. Set GROQ_MODEL to a current model "
                "(default in repo: llama-3.3-70b-versatile). See "
                "https://console.groq.com/docs/models"
            )
        elif DEBUG:
            err = str(e)
        else:
            err = "Persona generation failed. Check server logs."
        return jsonify({"success": False, "error": err}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=DEBUG)
