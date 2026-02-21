# adaptive_rag_web_fallback.py
import os
import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import requests

load_dotenv()

# === API Keys ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not OPENAI_API_KEY:
    st.error("Please set OPENAI_API_KEY")
    st.stop()
if not SERPAPI_KEY:
    st.warning("Web fallback disabled (no SERPAPI_KEY)")

# === Streamlit UI ===
st.title("Adaptive RAG + Web Fallback")

uploaded_pdfs = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
uploaded_excels = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

# === OpenAI embeddings and LLM ===
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)

# === Helper functions ===
def load_and_split_docs(pdf_files=[], excel_files=[]):
    docs = []
    for pdf in pdf_files:
        reader = PdfReader(pdf)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        docs.append(text)
    for excel in excel_files:
        df = pd.read_excel(excel)
        text = df.astype(str).apply(lambda x: " | ".join(x), axis=1).str.cat(sep="\n")
        docs.append(text)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splitted_docs = []
    for doc in docs:
        splitted_docs.extend(splitter.split_text(doc))
    return splitted_docs

def serp_search(query, k=3):
    """Return top-k snippets from SerpAPI"""
    if not SERPAPI_KEY:
        return ""
    url = "https://serpapi.com/search.json"
    params = {"q": query, "api_key": SERPAPI_KEY}
    resp = requests.get(url, params=params).json()
    organic = resp.get("organic_results", [])
    snippets = []
    for r in organic[:k]:
        snippet = r.get("snippet") or r.get("title")
        if snippet:
            snippets.append(snippet)
    return "\n".join(snippets)

# === Main logic: create vectorstore ===
vectorstore = None
if uploaded_pdfs or uploaded_excels:
    with st.spinner("Processing documents..."):
        docs = load_and_split_docs(uploaded_pdfs, uploaded_excels)
        vectorstore = Chroma.from_texts(docs, embeddings)
    st.success("Documents indexed!")

# === Prompt Template ===
prompt_template = """
You are an expert assistant. Use the retrieved context to answer the question.
If the context is insufficient, incorporate external knowledge.

Question: {question}
Context:
{context}

Answer:"""
prompt = PromptTemplate(input_variables=["question", "context"], template=prompt_template)

# === Streamlit Query ===
query = st.text_input("Ask a question:")
if st.button("Get Answer") and query:
    if vectorstore:
        with st.spinner("Retrieving from documents..."):
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=retriever,
                chain_type="stuff",
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )
            result = qa_chain(query)
            answer = result['result']
            source_docs = result.get('source_documents', [])

        # === Evaluate sufficiency ===
        if len(source_docs) == 0 or len(answer.strip()) < 20:
            # === Fallback to Web ===
            with st.spinner("Context insufficient, fetching web info..."):
                web_context = serp_search(query)
                if web_context:
                    combined_context = "\n".join([answer, web_context])
                    answer = llm.predict(f"Question: {query}\nContext:\n{combined_context}\nAnswer:")
                else:
                    answer = llm.predict(f"Question: {query}\nNo document or web info found, answer from general knowledge:")

        st.markdown(f"**Answer:** {answer}")
    else:
        st.warning("Please upload at least one PDF or Excel file.")
