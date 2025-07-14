# 🧠 Reddit User Persona Generator

This project analyzes Reddit users based on their public activity to generate detailed psychological and behavioral personas using LLMs like **Groq**.

---

## 🚀 Features

- 🔍 Scrapes user data (posts + comments) via Reddit API
- 🧹 Cleans and preprocesses using NLP (NLTK, TextBlob, Vader)
- 🧠 Sends text to LLM (Groq or Gemini) for personality analysis
- 🧾 Outputs a structured `.txt` persona report
- 🌐 Optional: Streamlit UI for interactive visualization

---

## 🛠️ Tech Stack

- **Python 3.9+**
- `praw`, `textblob`, `nltk`, `vaderSentiment`, `spacy`
- **Groq API** for persona generation
- `Streamlit` (optional) for frontend viewing

---

## 📂 Project Structure

```text
reddit-persona-generator/
│
├── main.py                  # 🔁 Entry point script
├── config.py                # 🔧 API keys and settings
├── requirements.txt         # 📦 Dependencies
├── .env.example             # 🌿 Sample env file (no secrets)
│
├── templates/
│   └── persona_template.txt # 📄 Output formatting template
│
├── output/
│   ├── spez_persona.txt     # 🧾 Sample output
│   └── sample_user2.txt
│
├── src/                     # 🔍 Core modules
│   ├── reddit_scraper.py
│   ├── data_processor.py
│   ├── persona_analyzer.py
│   ├── citation_manager.py
│   └── output_generator.py
│
├── utils/
│   ├── text_utils.py        # 🔡 Text cleaning, keywords, readability
│   └── validation.py
│
├── viewer_app.py            # 🌐 Streamlit viewer (optional)
└── README.md                # 📘 This file
```

## 🧪 How to Run
1. Clone the Repo

``` 
git clone https://github.com/yourusername/reddit-persona-generator.git
cd reddit-persona-generator

```

2. Setup Virtual Environment```


```
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux

```
3. Install Dependencies

```
pip install -r requirements.txt

```
4. Configure Environment .env

```
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=your_app_name
GROQ_API_KEY=your_groq_key
LLM_PROVIDER=groq
GROQ_MODEL=llama3-70b-8192

```

## 🧠 Generate a Persona

```
python main.py https://www.reddit.com/user/spez

```

## 🌐 Optional: Launch Viewer

```
streamlit run viewer_app.py

```

## 📌 Sample Output Snippet

```
Username: spez
Primary Interest: technology
Big Five Traits:
- Openness: 0.65
- Conscientiousness: 0.58
...
Top Communities: ModSupport, modnews, Snoo
Motivational Quote: Empowering others through knowledge and community

```