# ================= IMPORTS =================
import os
import re
import requests
import streamlit as st
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn.preprocessing import normalize
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

#  ================= THRESHOLDS =================
RETRIEVAL_CONFIDENCE_THRESHOLD = 0.6
# Confidence to trust Excel data
DOMAIN_SIMILARITY_THRESHOLD = 0.45
# Cosine similarity for same-domain vs different-

# ================= ENV =================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# ================= STREAMLIT =================
st.set_page_config(page_title="Excel Intelligence Agent", layout="wide")

# ================= SESSION =================
st.session_state.setdefault("messages", [])
st.session_state.setdefault("vectordb", None)
st.session_state.setdefault("excel_domain", None)
st.session_state.setdefault("excel_domain_embedding", None)
st.session_state.setdefault("pending_web_query", None)
st.session_state.setdefault("awaiting_web_confirm", False)
st.session_state.setdefault("mini_bot", None)

# ================= LLM =================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ================= EMBEDDINGS =================
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ================= LOGGING =================
def agent_log(msg):
    print(msg)

# ================= LOAD EXCEL =================
def load_excel(file):
    return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

# ================= VECTOR STORE =================
def build_vectorstore(df):
    rows = df.astype(str).apply(lambda r: " | ".join(r), axis=1).tolist()
    docs = [Document(page_content=row) for row in rows]
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    docs = splitter.split_documents(docs)
    return Chroma.from_documents(
        documents=docs,
        embedding=embedder,
        persist_directory="./chroma_excel"
    )
# ================= DOMAIN SUMMARY =================
def summarize_excel_domain(df):
    sample = df.head(5).astype(str).to_dict()
    prompt = f"""
Given this Excel data sample, describe in ONE short line
what this data is mainly about.

Data:
{sample}
"""
    return llm.invoke(prompt).content.strip()

# ================= DOMAIN EMBEDDING =================
def build_domain_embedding(df):
    text = " ".join(df.head(20).astype(str).apply(lambda r: " ".join(r), axis=1).tolist())
    emb = embedder.embed_query(text)
    return normalize(np.array(emb).reshape(1, -1))

def same_domain_semantic(query, domain_text, threshold=DOMAIN_SIMILARITY_THRESHOLD):
    domain_vec = normalize(np.array(embedder.embed_query(domain_text)).reshape(1, -1))
    query_vec = normalize(np.array(embedder.embed_query(query)).reshape(1, -1))
    sim = (query_vec @ domain_vec.T).item()
    agent_log(f"🧭 Semantic similarity: {sim:.3f} for query: '{query}'")
    return sim >= threshold, sim


# ================= INTENT =================
def classify_intent(q):
    return "GREETING" if q.lower().strip() in ["hi", "hello", "hey"] else "DATA_QUERY"

# ================= CRAG =================
def crag_verify(query, evidence):
    prompt = f"""
You are an Evidence Validator.

User Question:
{query}

Evidence:
{evidence}

Classify as STRONG, WEAK, or FAIL.
Return ONLY one word.
"""
    return llm.invoke(prompt).content.strip().upper()

# ================= NUMERIC DETECTION =================
def is_numeric_data(text):
    pattern = r"(\d[\d,.]*\s*(?:₹|\$|%|lakh|crore)?)"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    return len(matches) > 0

# ================= NUMERIC EXTRACTION =================
def extract_numeric_answer(web_context, query):
    prompt = f"""
The Excel does not have exact data.
Extract the numeric value for the following query from the text below:

Query:
{query}

Web Snippet:
{web_context}

Return only the numeric value with unit if available.
"""
    return llm.invoke(prompt).content.strip()

# ================= WEB SEARCH =================
def web_fallback(query):
    try:
        params = {"engine": "google", "q": query, "api_key": SERPAPI_KEY, "num": 5}
        res = requests.get("https://serpapi.com/search.json", params=params, timeout=10)
        data = res.json()
    except Exception as e:
        agent_log(f"❌ Web search failed: {e}")
        return "", []

    snippets, links = [], []
    for r in data.get("organic_results", []):
        if r.get("snippet"):
            snippets.append(r["snippet"])
            links.append(r.get("link"))
    return " ".join(snippets), links[:1]

# ================= RETRIVAL CONFIDENCE =================
def retrieval_confidence(docs, query):
    if not docs:
        return 0.0
    query_lower = query.lower()
    keywords = [w for w in re.findall(r"\w+", query_lower) if not w.isdigit()]
    match_count = 0
    for doc in docs:
        content_lower = doc.page_content.lower()
        hits = sum(1 for kw in keywords if kw in content_lower)
        if hits > 0:
            match_count += 1
    confidence = match_count / len(docs)
    agent_log(f"📊 Retrieval confidence: {confidence:.2f} for query: '{query}'")
    return confidence

 

# ================= AGENT HELPERS =================

def is_non_data_query(query):
    """
    Detect non-data queries like greetings or chit-chat
    """
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    return query.lower().strip() in greetings

def is_numeric_query(query):
    """
    Detect if query is likely numeric/financial
    """
    return is_numeric_data(query) or bool(re.search(r"\d", query))

# ================= ADAPTIVE RAG AGENT =================
def agent(query):
    agent_log("\n🧠 AGENT START")
    agent_log(f"🔍 Query: {query}")

    # ===== HANDLE NON-DATA QUERIES =====
    if is_non_data_query(query):
        return {"answer": "👋 Hello! askme question."}

    # ===== CHECK EXCEL UPLOADED =====
    if st.session_state.vectordb is None:
        return {"answer": "📂 Please upload an Excel file first."}

    # ===== RETRIEVE FROM EXCEL =====
    retriever = st.session_state.vectordb.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)
    context = "\n".join(d.page_content for d in docs) if docs else ""

    # ===== RETRIEVAL CONFIDENCE =====
    confidence = retrieval_confidence(docs, query)
    agent_log(f"📊 Retrieval confidence: {confidence:.2f} for query: '{query}'")

    # ===== IF HIGH CONFIDENCE, TRY EXCEL ANSWER =====
    if confidence >= RETRIEVAL_CONFIDENCE_THRESHOLD:
        # Extract numeric answer if query/data is numeric
        if is_numeric_query(query):
            answer = extract_numeric_answer(context, query)
        else:
            answer = llm.invoke(f"Answer ONLY from this Excel data:\n{context}\n\nQuestion: {query}").content

        # CRAG verification
        crag_result = crag_verify(query, answer)
        agent_log(f"🧪 CRAG (Excel): {crag_result}")

        if crag_result == "STRONG" or is_numeric_query(query):
            return {"answer": answer}
        else:
            return {"answer": "⚠️ Data exists but cannot be confidently verified."}

    # ===== LOW CONFIDENCE: DOMAIN CHECK =====
    domain_text = st.session_state.excel_domain
    same_domain, sim_score = same_domain_semantic(query, domain_text, threshold=DOMAIN_SIMILARITY_THRESHOLD)
    agent_log(f"🧭 Domain similarity: {sim_score:.3f} for query: '{query}'")

    # Only trigger web fallback for numeric/data queries in same domain
    if same_domain and is_numeric_query(query):
        web_context, links = web_fallback(query)
        if web_context:
            answer = extract_numeric_answer(web_context, query) if is_numeric_data(web_context) else \
                     llm.invoke(f"Answer using verified external data:\n{web_context}\n\nQuestion: {query}").content
            st.session_state.mini_bot = {
                "text": "Verified external source used (same domain)",
                "link": links[0] if links else None
            }
            return {"answer": answer}
        else:
            return {"answer": "❌ Unable to verify reliable data."}

    # Different domain or non-numeric → ask user for web search
    if not same_domain:
        st.session_state.pending_web_query = query
        st.session_state.awaiting_web_confirm = True
        return {
            "answer": f"⚠️ This Excel is about **{domain_text}**.\n"
                      f"Your question appears to be from a different domain.\n\n"
                      f"🔎 Click below if you want me to search the web."
        }

    # Default fallback
    return {"answer": "⚠️ Excel does not contain relevant data for this query."}




# ================= SIDEBAR =================
with st.sidebar:
    st.title("📂 Upload Excel")
    file = st.file_uploader("Upload CSV / Excel", ["csv", "xlsx"])
    if file:
        df = load_excel(file)
        st.session_state.vectordb = build_vectorstore(df)
        st.session_state.excel_domain = summarize_excel_domain(df)
        st.session_state.excel_domain_embedding = build_domain_embedding(df)
        st.success("✅ Excel uploaded and indexed")
        st.info(f"📊 This Excel is about: {st.session_state.excel_domain}")

# ================= CHAT UI =================
st.title("💬 Excel Intelligence Chat")
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

q = st.chat_input("Ask a question...")
if q:
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)

    res = agent(q)
    with st.chat_message("assistant"):
        st.markdown(res["answer"])
    st.session_state.messages.append({"role": "assistant", "content": res["answer"]})

# ================= WEB CONFIRMATION (DIFFERENT DOMAIN) =================
if st.session_state.awaiting_web_confirm:
    if st.button("🔎 Yes, search the web"):
        query = st.session_state.pending_web_query
        st.session_state.pending_web_query = None
        st.session_state.awaiting_web_confirm = False
        web_context, links = web_fallback(query)
        if web_context:
            if is_numeric_data(web_context):
                answer = extract_numeric_answer(web_context, query)
                st.session_state.mini_bot = {"text": "Verified numeric external source used", "link": links[0] if links else None}
            else:
                answer = llm.invoke(f"Answer ONLY from verified web data:\n{web_context}\n\nQuestion:{query}").content
                st.session_state.mini_bot = {"text": "Verified external web source", "link": links[0] if links else None}
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# ================= MINI BOT =================
if st.session_state.mini_bot:
    st.markdown(
        f"""
        <div style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #111;
        color: white;
        padding: 12px;
        border-radius: 10px;
        font-size: 13px;
        z-index: 999;
        ">
        🤖 {st.session_state.mini_bot['text']}<br>
        <a href="{st.session_state.mini_bot['link']}" target="_blank"
        style="color:#4da6ff">Open source</a>
        </div>
        """,
        unsafe_allow_html=True
    )
