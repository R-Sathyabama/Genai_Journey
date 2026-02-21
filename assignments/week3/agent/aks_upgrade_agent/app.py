import os
import re
import sqlite3
import requests
import streamlit as st
from typing import List
from bs4 import BeautifulSoup

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# =========================================================
# CONFIG
# =========================================================

OPENAI_MODEL = "gpt-4o-mini"
EMBEDDINGS = OpenAIEmbeddings()
LLM = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
DB_FILE = "upgrade_changes.db"

# =========================================================
# DATABASE INIT
# =========================================================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS changes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version TEXT,
        section TEXT,
        category TEXT,
        description TEXT
    )
    """)
    conn.commit()
    conn.close()

# =========================================================
# FETCH RAW MARKDOWN (Token Efficient)
# =========================================================

def convert_to_raw(url):
    if "github.com" in url:
        return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return url

def fetch_markdown(url):
    raw_url = convert_to_raw(url)
    r = requests.get(raw_url, timeout=30)
    if r.status_code != 200:
        return ""
    return r.text

# =========================================================
# DETERMINISTIC STRUCTURED PARSER
# =========================================================

def parse_release_notes(md_text, version):
    """
    Extracts ONLY:
    - Deprecated
    - Removed
    - API Changes
    - Behavior Changes
    - Security Fixes
    """
    sections = {
        "deprecated": [],
        "removed": [],
        "api": [],
        "behavior": [],
        "security": []
    }

    lines = md_text.split("\n")
    current_section = None

    for line in lines:
        lower = line.lower()

        if "deprecated" in lower:
            current_section = "deprecated"
        elif "removed" in lower:
            current_section = "removed"
        elif "api change" in lower:
            current_section = "api"
        elif "behavior" in lower:
            current_section = "behavior"
        elif "security" in lower:
            current_section = "security"

        if current_section and line.strip().startswith(("-", "*")):
            sections[current_section].append(line.strip())

    return sections

# =========================================================
# STORE INTO SQLITE
# =========================================================

def store_changes(version, parsed_sections):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    for category, items in parsed_sections.items():
        for item in items:
            c.execute("""
            INSERT INTO changes (version, section, category, description)
            VALUES (?, ?, ?, ?)
            """, (version, category, category, item))

    conn.commit()
    conn.close()

# =========================================================
# BUILD VECTOR STORE
# =========================================================

def build_vectorstore(documents: List[Document]):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)
    return FAISS.from_documents(chunks, EMBEDDINGS)

# =========================================================
# VERSION RANGE FILTER
# =========================================================

def get_changes_between(current_version, target_version):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    SELECT version, category, description
    FROM changes
    WHERE version > ? AND version <= ?
    """, (current_version, target_version))

    rows = c.fetchall()
    conn.close()
    return rows

# =========================================================
# RISK SCORING
# =========================================================

def compute_risk(changes):
    risk = "LOW"

    for v, cat, desc in changes:
        if cat == "removed":
            return "CRITICAL"
        if cat == "deprecated":
            risk = "MEDIUM"

    return risk

# =========================================================
# STRICT EXPLANATION LAYER
# =========================================================

def generate_explanation(question, changes, semantic_context, risk):
    structured = "\n".join(
        f"[{v}] ({cat}) {desc}" for v, cat, desc in changes
    )

    prompt = f"""
You are a Kubernetes upgrade specialist.

STRICT RULES:
- Use ONLY the structured changes below.
- If something is not present, say "Not found in release notes."
- Do NOT generalize.
- Do NOT add outside knowledge.

Structured Changes:
{structured}

Semantic Context:
{semantic_context}

Risk Level: {risk}

User Question:
{question}

Answer clearly in human-friendly language.
"""

    return LLM.invoke(prompt).content

# =========================================================
# STREAMLIT UI
# =========================================================

st.set_page_config(layout="wide")
st.title("🚀 Kubernetes Upgrade Intelligence (Production)")

init_db()

current_version = st.text_input("Current Version (e.g., 1.22.0)")
target_version = st.text_input("Target Version (e.g., 1.24.0)")

urls_input = st.text_area("Release Note URLs (one per line)")
urls = [u.strip() for u in urls_input.splitlines() if u.strip()]

if st.button("Ingest Release Notes"):
    for url in urls:
        version_match = re.search(r'CHANGELOG-(\d+\.\d+)', url)
        if not version_match:
            continue
        version = version_match.group(1)

        md = fetch_markdown(url)
        parsed = parse_release_notes(md, version)
        store_changes(version, parsed)

    st.success("Release notes ingested successfully!")

question = st.text_area("Ask Upgrade Question")

if st.button("Analyze Upgrade"):
    if not question:
        st.warning("Please ask a question.")
    else:
        changes = get_changes_between(current_version, target_version)

        # Build semantic context
        documents = [Document(page_content=row[2]) for row in changes]
        if documents:
            vectorstore = build_vectorstore(documents)
            semantic_docs = vectorstore.similarity_search(question, k=5)
            semantic_context = "\n".join(d.page_content for d in semantic_docs)
        else:
            semantic_context = ""

        risk = compute_risk(changes)

        answer = generate_explanation(
            question,
            changes,
            semantic_context,
            risk
        )

        st.markdown("## 🧾 Upgrade Report")
        st.write(answer)

        st.markdown(f"### ⚠ Overall Risk: {risk}")
