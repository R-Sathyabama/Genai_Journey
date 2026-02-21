import os
import streamlit as st
import pandas as pd
import faiss
import requests
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
import re

# ================= SETUP =================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

st.set_page_config(page_title="Gold & Silver Agentic RAG", layout="wide")
st.title("🧠 Gold & Silver Agentic RAG (CRAG + Fallback)")

# ================= FILE UPLOAD =================
uploaded_files = st.file_uploader(
    "Upload Excel / CSV (format with columns: date, year, month, bullion_type, price, grams)",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

# ================= LOAD & EMBED =================
@st.cache_resource
def load_data(files):
    texts = []
    df_full = pd.DataFrame()

    for f in files:
        df = pd.read_csv(f) if f.name.endswith(".csv") else pd.read_excel(f)
        df = df.astype(str)
        df_full = pd.concat([df_full, df], ignore_index=True)

        for _, row in df.iterrows():
            texts.append(" | ".join(row.values))

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return texts, index, model, df_full

# ================= RETRIEVAL =================
def retrieve(query, texts, index, model, k=5):
    q_emb = model.encode([query])
    _, ids = index.search(q_emb, k)
    return "\n".join([texts[i] for i in ids[0]])

# ================= CRAG VERIFICATION =================
def crag_verify(query, context):
    if not context.strip():
        return False

    prompt = f"""
You are a Corrective RAG (CRAG) verifier.

User Question:
{query}

Retrieved Context:
{context}

Is this context sufficient, correct, and directly answers the question?
Reply ONLY with YES or NO.
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip().upper() == "YES"

# ================= WEB FALLBACK =================
def web_search_price(bullion_type, date_obj):
    import re
    from datetime import datetime, date

    # Normalize date
    if isinstance(date_obj, str):
        date_obj = date_obj.replace("/", "-")
        date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()

    date_str = date_obj.strftime("%d %B %Y")

    query = f"{bullion_type} price in India on {date_str}"
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 5
    }

    resp = requests.get(url, params=params, timeout=10).json()
    snippets = [
        r.get("snippet", "") for r in resp.get("organic_results", [])
        if r.get("snippet")
    ]

    if not snippets:
        return "❌ No usable web results."

    combined = " ".join(snippets)

    # -------- GOLD --------
    if bullion_type.lower() == "gold":
        match = re.search(r"₹\s?([\d,]+)", combined)
        if match:
            price = match.group(1).replace(",", "")
            return f"Gold price on {date_str}: {price} INR (per 10 grams)"
        return "❌ No verified gold price found."

    # -------- SILVER --------
    if bullion_type.lower() == "silver":
        # Try per gram
        gram_match = re.search(r"₹\s?([\d,]+)\s*(?:per\s*gram|/g)", combined, re.I)
        if gram_match:
            per_gram = float(gram_match.group(1).replace(",", ""))
            per_kg = int(per_gram * 1000)
            return f"Silver price on {date_str}: {per_kg} INR (per kilogram)"

        # Try direct kg mention
        kg_match = re.search(r"₹\s?([\d,]+)\s*(?:per\s*kg|kilogram)", combined, re.I)
        if kg_match:
            price = kg_match.group(1).replace(",", "")
            return f"Silver price on {date_str}: {price} INR (per kilogram)"

        return "❌ No verified silver price found."


# ================= EXACT DATA RETRIEVAL =================
def retrieve_exact(df, bullion, year, month, date):
    df_filtered = df[df['bullion_type'].str.lower() == bullion.lower()]
    df_filtered = df_filtered[df_filtered['year'] == str(year)]
    df_filtered = df_filtered[df_filtered['month'].str.lower() == month.lower()]
    df_filtered = df_filtered[df_filtered['date'] == str(date)]

    if df_filtered.empty:
        return None

    row = df_filtered.iloc[0]
    return f"{row['bullion_type']} price on {row['date']} {row['month']} {row['year']}: {row['price']} INR ({row['grams']})"

# ================= AGENT LOGIC =================
def agent_answer(query, df, texts, index, model, bullion, date_input):
    today = datetime.today()

    # Parse date_input from date picker widget
    try:
        date_obj = datetime.strptime(date_input, "%Y-%m-%d")
    except Exception:
        return "❌ Invalid date format. Please select a date from the picker."

    # Extract date components
    year = date_obj.year
    month = date_obj.strftime("%B")  # Full month name, e.g., 'February'
    date = date_obj.day

    # Polite block for future dates
    if date_obj > today:
        return f"❌ Cannot provide data for future date {date_input}."

    # Try historical uploaded data
    hist_answer = retrieve_exact(df, bullion, year, month, date)
    if hist_answer:
        if crag_verify(query, hist_answer):
            return f"📘 Answer from uploaded data:\n{hist_answer}"
        else:
            return f"📘 Answer from uploaded data (unverified by CRAG):\n{hist_answer}"

    # Fall back to web for past/present only
    web_answer = web_search_price(bullion_type, date_obj)
    if crag_verify(query, web_answer):
        return f"🌐 Answer from verified web data:\n{web_answer}"
    return f"🌐 Answer from web:\n{web_answer}"

# ================= STREAMLIT UI =================
if uploaded_files:
    with st.spinner("Indexing data..."):
        texts, index, model, df_data = load_data(uploaded_files)
    st.success("Data indexed successfully!")

    col1, col2 = st.columns(2)
    with col1:
        bullion_type = st.selectbox("Select Bullion", ["Gold", "Silver"])
    with col2:
        date_input = st.date_input(
            "Pick a date (past/present only)",
            max_value=datetime.today()
        ).strftime("%Y-%m-%d")

    if st.button("Get Price"):
        with st.spinner("Thinking like an agent..."):
            answer = agent_answer(
                f"{bullion_type} price on {date_input}",
                df_data, texts, index, model,
                bullion_type, date_input
            )
        st.subheader("Answer")
        st.write(answer)
else:
    st.info("Upload at least one Excel/CSV file with correct columns to begin.")


  


