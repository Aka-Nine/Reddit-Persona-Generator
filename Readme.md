# 🧠 Reddit User Persona Generator

> **An AI-powered Python tool that scrapes a Reddit user's public activity and generates a detailed psychological and behavioral persona — complete with Big Five personality scores, citations, and an interactive Streamlit viewer.**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![PRAW](https://img.shields.io/badge/PRAW-Reddit%20API-ff4500?style=flat&logo=reddit&logoColor=white)](https://praw.readthedocs.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA3%2FMixtral-f97316?style=flat)](https://groq.com)
[![Gemini](https://img.shields.io/badge/Gemini-Google%20AI-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![NLP](https://img.shields.io/badge/NLP-NLTK%20·%20spaCy%20·%20TextBlob-8b5cf6?style=flat)](https://nltk.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture Diagram](#-architecture-diagram)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Persona Output Format](#-persona-output-format)
- [Sample Output](#-sample-output)
- [Environment Variables](#-environment-variables)
- [Installation](#-installation)
- [Usage](#-usage)
- [Web UI & Docker](#-web-ui--docker)
- [CI/CD (GitHub Actions)](#cicd-github-actions)
- [Streamlit Viewer](#-streamlit-viewer)
- [Configuration Reference](#-configuration-reference)
- [Testing](#-testing)
- [Ethical Considerations](#-ethical-considerations)
- [Known Limitations](#-known-limitations)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)

---

## 🧠 Overview

The **Reddit User Persona Generator** is a modular, LLM-powered analysis pipeline that turns a Reddit profile URL into a rich psychological and behavioral profile. It combines traditional NLP techniques (sentiment analysis, entity extraction, keyword scoring) with a large language model to produce structured, cited persona reports.

The system is designed to be **provider-agnostic** — you can swap between **Groq** (LLaMA3-70B / Mixtral-8x7B for ultra-fast inference) and **Google Gemini** simply by changing an environment variable. An optional **Streamlit frontend** renders the `.txt` persona output as an interactive, expandable web dashboard.

**Use cases include:** user research, behavioral analysis, community moderation insights, LLM fine-tuning dataset creation, and UX persona development.

---

## 🏛️ Architecture Diagram

![System Architecture](./architecture.svg)

> The pipeline flows through four layers: **Input** (CLI + config), **Scraping** (Reddit API via PRAW), **NLP + AI** (multi-library NLP enrichment → LLM persona synthesis → citation linking), and **Output** (structured `.txt` report + Streamlit viewer).

---

## ✨ Features

- **Reddit Scraping** — Fetches up to 100 posts and 200 comments from any public Reddit profile via PRAW with built-in rate limiting
- **Multi-library NLP Pipeline** — NLTK tokenization, TextBlob sentiment, VADER polarity, spaCy NER, and keyword extraction all run before the LLM call
- **Dual LLM Support** — Groq (LLaMA3-70B / Mixtral-8x7B-32768) as default, Google Gemini as alternate — switchable via environment variable
- **Big Five Personality Scoring** — Generates Openness, Conscientiousness, Extraversion, Agreeableness, and Neuroticism scores (0.0–1.0)
- **Cited Persona Traits** — Every inferred trait links back to specific posts or comments (up to 3 citations per trait, configurable)
- **Structured Template Output** — Consistent `.txt` persona format via `persona_template.txt`, saved to `output/{username}_persona.txt`
- **Interactive Streamlit Viewer** — `visualizer.py` parses the output file and renders it as a web dashboard with expandable sections and a summary sidebar
- **Modular Architecture** — Clean separation across `reddit_scraper`, `data_processor`, `persona_analyzer`, `citation_manager`, and `output_generator`
- **Validated Config** — `config.py` validates required env vars at startup and throws helpful errors for missing keys

---

## 🛠️ Tech Stack

### Core

| Technology | Role |
|---|---|
| **Python 3.9+** | Core language |
| **PRAW** | Reddit API wrapper — fetches posts and comments |
| **python-dotenv** | Loads environment variables from `.env` |

### NLP

| Technology | Role |
|---|---|
| **NLTK** | Tokenization, stopword removal, frequency distribution |
| **TextBlob** | Polarity + subjectivity sentiment scoring |
| **VADER (vaderSentiment)** | Fine-grained social-media-optimized sentiment analysis |
| **textstat** | Readability scoring (used in `text_utils.py`) |
| **text_utils.py** | Custom keyword extraction and readability scoring |

### LLM Providers

| Provider | Model | Notes |
|---|---|---|
| **Groq** *(default)* | `mixtral-8x7b-32768`, `llama3-70b-8192` | Ultra-fast inference, 32K context window |
| **Google Gemini** *(alternate)* | `gemini-pro` | Switch via `LLM_PROVIDER=google` |

### Frontend & API

| Technology | Role |
|---|---|
| **Flask** | Web UI + `POST /analyze` API (`server.py`, `static/`) — use same host/port as the page to avoid CORS issues |
| **Streamlit** | Optional viewer for persona `.txt` output (`pip install -r requirements-streamlit.txt`) |

### Deploy

| Technology | Role |
|---|---|
| **Docker / gunicorn** | `Dockerfile`, `docker-compose.yml`, `Procfile` for production |
| **GitHub Actions** | CI (pytest + image build) and CD (push to `ghcr.io` on tags) — see [CI/CD](#cicd-github-actions) |

---

## 📁 Project Structure

```
Reddit-Persona-Generator/
│
├── main.py                        # CLI — orchestrates the full pipeline
├── server.py                      # Flask API + static web UI
├── config.py                      # Centralized config & env var validation
├── visualizer.py                  # Optional Streamlit persona viewer
├── requirements.txt               # App dependencies (production)
├── requirements-streamlit.txt    # Optional Streamlit stack
├── Dockerfile                     # Container image
├── docker-compose.yml             # Local/prod compose (env_file: `.env`)
├── Procfile                       # Heroku-style gunicorn entry
├── runtime.txt                    # Python version hint (e.g. Heroku)
├── .env.example                   # Sample env (copy to `.env`)
├── .github/workflows/             # CI/CD (pytest, Docker build, GHCR push)
├── .gitignore                     # Excludes `.env`, `__pycache__`, etc.
│
├── src/                           # Core pipeline modules
│   ├── reddit_scraper.py          # PRAW-based Reddit data fetcher
│   ├── data_processor.py          # Text cleaning, filtering, normalization
│   ├── persona_analyzer.py        # NLP analysis + LLM persona generation
│   ├── citation_manager.py        # Links persona traits to source content
│   └── output_generator.py        # Formats and writes final persona report
│
├── utils/
│   ├── text_utils.py              # Keyword extraction, readability scoring
│   ├── validation.py              # URL validation, input sanitization
│   └── reddit_url.py              # Shared Reddit username/URL parsing (CLI + server)
│
├── static/
│   └── index.html                 # Web UI (served by Flask)
│
├── templates/
│   └── persona_template.txt       # Output format template
│
├── output/                        # Generated persona `.txt` files
│   └── …                          # e.g. `spez_persona.txt`
│
├── tests/
│   ├── test_scraper.py
│   └── test_analyser.py
│
├── info.txt                       # Project notes
└── Readme.md
```

---

## 🔄 How It Works

### Full Pipeline (Step by Step)

```
1. INPUT
   User runs: python main.py https://www.reddit.com/user/spez
       │
       ├── config.py validates env vars (raises ValueError if missing)
       └── URL parsed → username extracted ("spez")

2. SCRAPING  (reddit_scraper.py)
       │
       ├── Authenticate with Reddit OAuth2 (read-only)
       ├── Fetch up to MAX_POSTS=100 recent submissions
       ├── Fetch up to MAX_COMMENTS=200 recent comments
       ├── Apply SCRAPING_DELAY=1.0s between requests
       └── Return raw post/comment objects

3. CLEANING  (data_processor.py + utils/)
       │
       ├── Remove deleted/removed content
       ├── Filter short content: MIN_TEXT_LENGTH=10
       ├── Truncate long content: MAX_TEXT_LENGTH=4000
       ├── Strip URLs, markdown, special characters
       └── Return clean structured text corpus

4. NLP ENRICHMENT  (persona_analyzer.py)
       │
       ├── NLTK: tokenize, stopword removal, frequency dist
       ├── TextBlob: polarity + subjectivity per post
       ├── VADER: compound sentiment score per comment
       ├── spaCy: extract named entities (ORG, GPE, PERSON)
       ├── text_utils.py: top keywords, readability score
       └── Pre-score Big Five traits from linguistic signals

5. LLM PERSONA GENERATION  (persona_analyzer.py → Groq / Gemini)
       │
       ├── Bundle NLP features + raw text sample → prompt
       ├── Send to LLM (Groq default, Gemini alternate)
       ├── LLM returns structured persona fields:
       │   demographics, personality, interests, style,
       │   motivations, frustrations, goals, quote
       └── Parse LLM response

6. CITATION LINKING  (citation_manager.py)
       │
       ├── For each inferred trait, find supporting posts/comments
       ├── Score relevance, pick top CITATION_LIMIT=3
       └── Attach source links and excerpts to each trait

7. OUTPUT  (output_generator.py)
       │
       ├── Apply persona_template.txt formatting
       ├── Insert all fields + citations
       ├── Write to output/{username}_persona.txt
       └── Print summary to stdout

8. OPTIONAL: STREAMLIT VIEWER  (visualizer.py)
       │
       ├── streamlit run visualizer.py
       ├── Load persona .txt file
       ├── Parse into sections via regex
       ├── Render expandable panels + sidebar stats
       └── Serve at http://localhost:8501
```

---

## 📊 Persona Output Format

Each generated persona report follows this structured template:

```
USERNAME
========

DEMOGRAPHICS
============
Estimated Age:       25–34
Occupation:          Software Engineer (inferred)
Location:            United States (inferred)
Relationship Status: Not specified

PERSONALITY TRAITS
==================
Big Five Scores:
  Openness:           0.78
  Conscientiousness:  0.62
  Extraversion:       0.41
  Agreeableness:      0.55
  Neuroticism:        0.33

PRIMARY INTERESTS
=================
1. Technology / Programming
2. Gaming
3. Finance / Investing
[Citations: post_id_1, post_id_2]

WRITING STYLE
=============
Tone:           Analytical, occasionally sarcastic
Avg Sentiment:  0.14 (mildly positive)
Complexity:     High readability score
Common Terms:   ["API", "latency", "async", ...]

MOTIVATIONS & GOALS
===================
...

FRUSTRATIONS
============
...

ACTIVITY SUMMARY
================
Primary Interest:  technology
Activity Level:    Very Active (high post frequency)
Top Subreddits:    r/programming, r/investing, r/gaming
Confidence Score:  0.84

CITATIONS
=========
[1] r/programming – "The async/await pattern in Python is..."
[2] r/personalfinance – "I've been DCAing into index funds..."
```

---

## 📸 Sample Output

```
Username: spez
Primary Interest: technology
Big Five Traits:
  Openness: 0.65
  Conscientiousness: 0.58
  Extraversion: 0.72
  Agreeableness: 0.44
  Neuroticism: 0.29

Top Communities: r/ModSupport, r/modnews, r/announcements
Activity Level: Extremely Active
Motivational Quote: "Empowering others through knowledge and community"
Confidence Score: 0.81
```

Full persona files are in the `output/` directory.

---

## ⚙️ Environment Variables

Create a `.env` file in the project root. All required variables are validated by `config.py` at startup.

```env
# ── Reddit API (required) ──────────────────────────────────────────────
# Get these from: https://www.reddit.com/prefs/apps → "create another app"
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=PersonaGenerator:v1.0.0 (by /u/your_reddit_username)

# ── LLM Provider (choose one) ─────────────────────────────────────────
LLM_PROVIDER=groq                  # 'groq' (default) or 'google'
GROQ_API_KEY=your_groq_api_key     # https://console.groq.com
GOOGLE_API_KEY=your_google_api_key # https://ai.google.dev (if using Gemini)

# ── Model Selection ───────────────────────────────────────────────────
GROQ_MODEL=mixtral-8x7b-32768      # or: llama3-70b-8192
GOOGLE_MODEL=gemini-pro

# ── Scraping Limits ───────────────────────────────────────────────────
MAX_POSTS=100
MAX_COMMENTS=200
SCRAPING_DELAY=1.0                 # Seconds between API calls

# ── Analysis Settings ─────────────────────────────────────────────────
MIN_TEXT_LENGTH=10                 # Ignore very short posts
MAX_TEXT_LENGTH=4000               # Truncate very long posts
CONFIDENCE_THRESHOLD=0.7           # Minimum confidence for a trait to be included

# ── Output Settings ───────────────────────────────────────────────────
OUTPUT_DIR=output
INCLUDE_CITATIONS=True
CITATION_LIMIT=3                   # Max citations per trait

# ── Logging ───────────────────────────────────────────────────────────
LOG_LEVEL=INFO
LOG_FILE=persona_generator.log
```

---

## 🚀 Installation

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Aka-Nine/Reddit-Persona-Generator.git
cd Reddit-Persona-Generator
```

### Step 2 — Create a Virtual Environment

```bash
python -m venv venv

# Activate:
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Download NLP Models

```bash
# NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# spaCy English model
python -m spacy download en_core_web_sm
```

### Step 5 — Create a Reddit App

1. Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click **"create another app"**
3. Choose **"script"** type
4. Set redirect URI to `http://localhost:8080`
5. Copy your **Client ID** (under the app name) and **Client Secret**

### Step 6 — Configure .env

```bash
cp .env.example .env
# Edit .env with your API keys
```

---

## 💻 Usage

### Generate a Persona (CLI)

```bash
# Using a full Reddit profile URL
python main.py https://www.reddit.com/user/spez

# Output saved to: output/spez_persona.txt
```

### Multiple Users

```bash
python main.py https://www.reddit.com/user/spez
python main.py https://www.reddit.com/user/GallowBoob
python main.py https://www.reddit.com/user/kojied
```

### Switch LLM Provider

```bash
# Use Google Gemini instead of Groq
LLM_PROVIDER=google python main.py https://www.reddit.com/user/spez

# Or set in .env:
LLM_PROVIDER=google
GOOGLE_API_KEY=your_key_here
```

---

## 🌐 Web UI & Docker

Run the **Flask** app so the browser and `POST /analyze` share the same origin (avoids CORS / empty JSON responses):

```bash
python server.py
```

Open `http://127.0.0.1:5000/` (or the URL shown in the terminal). Use the same `.env` variables as the CLI.

**Health checks:** `GET /health` or `GET /healthz`.

### Docker

```bash
docker build -t persona-gen .
docker run --rm --env-file .env -p 8080:8080 persona-gen
```

Or: `docker compose up --build` (loads `.env`, sets `OUTPUT_DIR=/tmp/output` in the container).

**Windows:** `requirements.txt` must be **UTF-8** (not UTF-16). If pip or Docker shows `\x00` in errors, re-save the file as UTF-8.

**PaaS:** On Heroku, Railway, or Render, set env vars from `.env.example`, use the `Dockerfile` or `Procfile`, and set `OUTPUT_DIR=/tmp/output` if only `/tmp` is writable. **CORS:** use `CORS_ORIGINS=https://your-frontend.com` when the UI is on another origin. **Timeouts:** persona runs can exceed 30s — the image and `Procfile` use gunicorn `--timeout 180`.

---

## CI/CD (GitHub Actions)

| Workflow | When | What |
|---|---|---|
| **CI** (`.github/workflows/ci.yml`) | Push / PR to `main` or `master` | `pytest` + Docker **build** (no push) |
| **CD** (`.github/workflows/cd.yml`) | Git tag `v*` (e.g. `v1.0.0`) or **Run workflow** in Actions | Build and **push** image to **GHCR** (`ghcr.io/<owner>/<repo>`) |
| **Dependabot** (`.github/dependabot.yml`) | Weekly / monthly | PRs for pip and GitHub Actions updates |

**One-time:** Repo **Settings → Actions → General → Workflow permissions** — allow **read and write** (or `packages: write`) so `GITHUB_TOKEN` can push to GHCR.

**Release:** `git tag v1.0.0 && git push origin v1.0.0` → image tags include `v1.0.0` and `latest`. **Manual run:** Actions → **CD** → **Run workflow** (optional extra tag via input).

**Adding new checks:** edit `.github/workflows/ci.yml` (e.g. add `ruff`, matrix Python versions, or a job that runs `docker compose run`).

---

## 🌐 Streamlit Viewer

Launch the interactive persona viewer to browse generated profiles in a web UI:

```bash
streamlit run visualizer.py
```

The viewer will open at `http://localhost:8501`. Features:

- **File picker** — enter the path to any `output/*.txt` persona file
- **Expandable sections** — each persona category (Demographics, Personality, Interests, etc.) is collapsible
- **Auto-expanded** — "Analysis Summary" and "Personality Traits" sections open by default
- **Sidebar** — shows Primary Interest, Activity Level, and Confidence Score at a glance

---

## ⚙️ Configuration Reference

All settings are managed via `config.py` with environment variable overrides:

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `groq` | LLM backend: `groq` or `google` |
| `GROQ_MODEL` | `mixtral-8x7b-32768` | Groq model ID |
| `GOOGLE_MODEL` | `gemini-pro` | Gemini model ID |
| `MAX_POSTS` | `100` | Max submissions to fetch |
| `MAX_COMMENTS` | `200` | Max comments to fetch |
| `SCRAPING_DELAY` | `1.0` | Seconds between Reddit API calls |
| `MIN_TEXT_LENGTH` | `10` | Skip posts shorter than this |
| `MAX_TEXT_LENGTH` | `4000` | Truncate posts longer than this |
| `CONFIDENCE_THRESHOLD` | `0.7` | Minimum trait confidence to include |
| `INCLUDE_CITATIONS` | `True` | Attach source references to traits |
| `CITATION_LIMIT` | `3` | Max citations per trait |
| `OUTPUT_DIR` | `output` | Directory for persona `.txt` files |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## 🧪 Testing

Run the unit tests with pytest:

```bash
pip install pytest
pytest tests/ -v
```

Test coverage includes:

- `test_scraper.py` — PRAW fetching, rate limiting, error handling (404, private profiles)
- `test_processor.py` — Text cleaning, filtering, length constraints
- `test_analyzer.py` — NLP scoring correctness, LLM prompt construction
- `test_output.py` — Template rendering, file writing, citation formatting

Run a specific test file:

```bash
pytest tests/test_scraper.py -v
```

---

## ⚖️ Ethical Considerations

This tool only accesses **publicly available** Reddit content. No private messages, direct messages, or non-public data are ever fetched.

**Please keep the following in mind when using this tool:**

- Generated personas are **AI inferences**, not definitive psychological profiles. They should be interpreted with appropriate skepticism.
- Do not use generated personas to harass, discriminate against, or make decisions about real individuals.
- Respect Reddit's [API Terms of Service](https://www.redditinc.com/policies/data-api-terms) and [User Agreement](https://www.redditinc.com/policies/user-agreement). Do not scrape at rates that violate these terms.
- If you are analyzing a profile and the user wishes to opt out, respect their request and delete the generated data.
- The `SCRAPING_DELAY` default of 1 second is intentionally conservative — do not reduce this significantly.

---

## ⚠️ Known Limitations

- **Private profiles** return no data — the script exits gracefully with a clear error message
- **Low-activity users** (few posts/comments) may produce low-confidence or incomplete personas
- **LLM accuracy** varies — inferred demographics (age, location, occupation) are estimates and may be wrong
- **Groq rate limits** apply on free-tier accounts — processing very large datasets may require pausing between users
- **spaCy NER** is English-only by default; non-English content may produce inaccurate entity extractions
- The output is plain text — no JSON export yet (on the roadmap)

---

## 🔮 Roadmap

- [ ] **JSON / structured output** — Export personas as JSON for downstream use
- [ ] **Batch processing** — Analyze multiple users from a list file in one run
- [ ] **Trend analysis** — Track persona evolution over time with historical snapshots
- [ ] **Multi-language support** — spaCy model selector for non-English users
- [ ] **Web UI upload** — Streamlit form to paste URL and generate persona in-browser
- [ ] **Async scraping** — Parallel fetching for faster data collection
- [ ] **Comparative analysis** — Diff two personas side by side
- [ ] **PDF export** — Render the persona report as a formatted PDF
- [ ] **LLM agent architecture** — Specialized sub-agents per personality dimension (demographics agent, interests agent, etc.)

---

## 🤝 Contributing

Contributions are welcome! To get started:

```bash
# Fork the repo, then:
git clone https://github.com/<your-username>/Reddit-Persona-Generator.git
cd Reddit-Persona-Generator

# Create a feature branch
git checkout -b feature/your-feature-name

# Install dependencies
pip install -r requirements.txt

# Make your changes and run tests
pytest tests/ -v

# Commit and push
git commit -m "feat: describe your change"
git push origin feature/your-feature-name

# Open a Pull Request on GitHub
```

Please ensure tests pass before opening a PR. Add new tests for any new functionality.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [PRAW](https://praw.readthedocs.io/) — the Python Reddit API Wrapper that makes scraping clean and easy
- [Groq](https://groq.com/) — blazing-fast LLM inference for Mixtral and LLaMA3
- [Google Gemini](https://ai.google.dev/) — powerful alternate LLM provider
- [NLTK](https://nltk.org/) · [spaCy](https://spacy.io/) · [TextBlob](https://textblob.readthedocs.io/) · [VADER](https://github.com/cjhutto/vaderSentiment) — the NLP backbone
- [Streamlit](https://streamlit.io/) — rapid interactive web UI with zero frontend code

---

<div align="center">

**Turning Reddit activity into actionable psychological insights — powered by NLP and LLMs.**

[⭐ Star this repo](https://github.com/Aka-Nine/Reddit-Persona-Generator) · [🐛 Report a bug](https://github.com/Aka-Nine/Reddit-Persona-Generator/issues) · [💡 Request a feature](https://github.com/Aka-Nine/Reddit-Persona-Generator/issues)

</div>
