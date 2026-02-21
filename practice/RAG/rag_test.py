
import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from dotenv import load_dotenv

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq

# -------------------------------------------------
# Setup
# -------------------------------------------------
load_dotenv()

st.set_page_config(page_title="Adaptive RAG App", layout="centered")
st.title("🧠 Adaptive RAG – PDF & Excel Q&A")

# Debug toggle (OFF by default)
debug_mode = st.checkbox("🔍 Show internal reasoning (debug mode)")

mode = st.radio(
    "Choose data source",
    ["PDF Document", "Excel Document"]
)

# -------------------------------------------------
# Models
# -------------------------------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# -------------------------------------------------
# 1️⃣ Query Analysis & Classification (INTERNAL)
# -------------------------------------------------
def classify_query(query: str) -> str:
    prompt = f"""
Classify the user question into ONE category:
- no_rag : greeting, definition, general question
- rag : needs factual lookup from data
- summary : wants summary or overview
- calculation : numeric or financial calculation

Return ONLY one word.

Question: {query}
"""
    return llm.invoke(prompt).content.strip().lower()

# -------------------------------------------------
# 2️⃣ Dynamic Strategy + 3️⃣ Dynamic Parameters
# -------------------------------------------------
def adaptive_answer(query, vectordb):
    query_type = classify_query(query)

    if debug_mode:
        st.info(f"🧠 Query type detected: **{query_type}**")

    # ---- Strategy selection ----
    if query_type == "no_rag":
        return llm.invoke(query).content

    elif query_type == "summary":
        retriever = vectordb.as_retriever(search_kwargs={"k": 6})
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever
        )
        return qa.run(f"Summarize the following data: {query}")

    elif query_type == "calculation":
        retriever = vectordb.as_retriever(search_kwargs={"k": 8})
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever
        )
        text = qa.run(query)

        # Simple numeric extraction
        numbers = [float(n) for n in re.findall(r"\d+\.?\d*", text)]
        if numbers:
            return f"Calculated result based on the data: {sum(numbers)}"
        else:
            return text

    else:  # normal RAG
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever
        )
        return qa.run(query)

# =================================================
# PDF MODE
# =================================================
if mode == "PDF Document":
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_pdf:
        raw_text = ""
        reader = PdfReader(uploaded_pdf)

        for page in reader.pages:
            if page.extract_text():
                raw_text += page.extract_text()

        if not raw_text.strip():
            st.error("❌ No readable text found in PDF")
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = splitter.split_text(raw_text)

            vectordb = Chroma.from_texts(
                chunks,
                embedding=embeddings,
                persist_directory="chroma_pdf"
            )

            st.success(f"✅ PDF loaded & split into {len(chunks)} chunks")

            query = st.text_input("Ask a question about the PDF")

            if query:
                with st.spinner("Thinking..."):
                    answer = adaptive_answer(query, vectordb)

                st.subheader("📌 Answer")
                st.write(answer)

# =================================================
# EXCEL MODE
# =================================================
if mode == "Excel Document":
    uploaded_excel = st.file_uploader(
        "Upload Excel file",
        type=["xlsx", "xls"]
    )

    if uploaded_excel:
        df = pd.read_excel(uploaded_excel)
        st.subheader("📊 Data Preview")
        st.dataframe(df.head())

        # Convert rows to text
        excel_text = []
        for _, row in df.iterrows():
            row_text = ", ".join(f"{col}: {row[col]}" for col in df.columns)
            excel_text.append(row_text)

        vectordb = Chroma.from_texts(
            excel_text,
            embedding=embeddings,
            persist_directory="chroma_excel"
        )

        query = st.text_input(
            "Ask (e.g. How much haliday in March?)"
        )

        if query:
            with st.spinner("Analyzing..."):
                answer = adaptive_answer(query, vectordb)

            st.subheader("📌 Answer")
            st.write(answer)
