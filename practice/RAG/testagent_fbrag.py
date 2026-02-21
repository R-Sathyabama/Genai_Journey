import os
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
import requests
from sentence_transformers import SentenceTransformer
import faiss
from dotenv import load_dotenv

load_dotenv()

# === API keys ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# === Load PDF & create index ===
@st.cache_resource
def load_pdfs_and_create_index(pdf_paths):
    docs = []
    for path in pdf_paths:
        reader = PdfReader(path)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        docs.append(text)
    chunks = []
    for doc in docs:
        for i in range(0, len(doc), 500):
            chunk = doc[i:i+500]
            if chunk.strip():
                chunks.append(chunk)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    vectors = model.encode(chunks)
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    return chunks, index, model

# === Retrieve ===
def retrieve(query, chunks, index, model, top_k=3):
    q_emb = model.encode([query])
    D, I = index.search(q_emb, top_k)
    return [chunks[i] for i in I[0]]

# === Verifier ===
def is_answer_sufficient(query, answer):
    prompt = f"""
Question: {query}
Retrieved Answer: {answer}
Is the retrieved answer sufficient, accurate, and complete? Reply with YES or NO and a short reason.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

# === Fallback: SerpAPI ===
def serp_search(query):
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY
    }
    resp = requests.get(url, params=params)
    results = resp.json()
    organic = results.get("organic_results", [])
    snippets = [r.get("snippet") or r.get("title") for r in organic if r.get("snippet") or r.get("title")]
    if snippets:
        return "\n".join(snippets)
    else:
        fallback_prompt = f"""
The web search for the question "{query}" returned no relevant results.
Please generate a helpful answer to this question using your general knowledge.
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": fallback_prompt}]
        )
        return response.choices[0].message["content"]

# === Orchestrator ===
def answer_query(query, chunks, index, model):
    retrieved = retrieve(query, chunks, index, model)
    combined = "\n\n".join(retrieved)
    verdict = is_answer_sufficient(query, combined)
    if "YES" in verdict.upper():
        return f"**From PDF:**\n\n{combined}\n\n**Verifier:** {verdict}"
    else:
        serp_result = serp_search(query)
        return f"**From Web:**\n\n{serp_result}\n\n**Verifier:** {verdict}"

# === Streamlit UI ===
st.title("Agentic RAG (PDF + Web fallback)")

uploaded_files = st.file_uploader(
    "Upload your PDF(s)", type=["pdf"], accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("Processing PDFs..."):
        pdf_paths = []
        for uploaded_file in uploaded_files:
            path = f"./tmp_{uploaded_file.name}"
            with open(path, "wb") as f:
                f.write(uploaded_file.read())
            pdf_paths.append(path)
        chunks, index, model = load_pdfs_and_create_index(pdf_paths)
    st.success("PDFs indexed!")

    query = st.text_input("Ask a question:")
    if st.button("Get Answer") and query:
        with st.spinner("Answering..."):
            answer = answer_query(query, chunks, index, model)
        st.markdown(answer)
