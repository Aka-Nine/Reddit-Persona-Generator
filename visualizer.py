import streamlit as st
import re
from pathlib import Path

st.set_page_config(page_title="Reddit User Persona Viewer", layout="wide")

st.title("🧠 Reddit User Persona Profile")
st.markdown("---")

# Load template file or persona output
def load_persona_text(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error("Persona file not found.")
        return ""

# Load default persona file from output
persona_file = st.text_input("Path to Persona File:", value="output/spez_persona.txt")
raw_text = load_persona_text(persona_file)

if not raw_text:
    st.stop()

# Split into sections
sections = re.split(r"\n([A-Z &]+)\n=+\n", raw_text)

if len(sections) < 3:
    st.warning("Could not parse structured sections from the file.")
    st.text_area("Raw Content:", raw_text, height=400)
    st.stop()

# Render structured view
st.markdown("## 👤 Persona Overview")
st.markdown(f"**Username:** `{sections[2].splitlines()[0]}`")

for i in range(1, len(sections) - 1, 2):
    section_title = sections[i].title()
    section_body = sections[i + 1].strip()

    with st.expander(f"📌 {section_title}", expanded=(section_title in ["Analysis Summary", "Personality Traits"])):
        st.markdown(f"```text\n{section_body}\n```")

# Sidebar for quick info
st.sidebar.header("📋 Summary")
if "Primary Interest" in raw_text:
    match = re.search(r"Primary Interest:\s*(\w+)", raw_text)
    if match:
        st.sidebar.write("**Primary Interest:**", match.group(1))

if "Activity Level" in raw_text:
    match = re.search(r"Activity Level:\s*([\w\s,]+)", raw_text)
    if match:
        st.sidebar.write("**Activity Level:**", match.group(1))

if "Confidence Score" in raw_text:
    match = re.search(r"Confidence Score:\s*(\d\.\d+)", raw_text)
    if match:
        st.sidebar.write("**Confidence Score:**", match.group(1))

st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ by your Persona Bot")
