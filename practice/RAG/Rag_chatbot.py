"""
#rag chat bot with fiass ,openai
import streamlit as st
from PyPDF2 import PdfReader
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

from langchain_community.vectorstores import FAISS
# from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os
load_dotenv()
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"),model_name="gpt-4o-mini", temperature=0.2)
embeddings = OpenAIEmbeddings()
st.title("RAG App: Ask Your PDF Anything")
uploaded_file = st.file_uploader("Upload your PDF document", type=["pdf"])
if uploaded_file is not None:
    raw_text = ""
    try:
        pdf_reader = PdfReader (uploaded_file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                raw_text += text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
    if not raw_text.strip():
        st.error(
            "Could not extract any text from this PDF.\n\n"
            "It may be a scanned image PDF with no selectable text.\n\n"
            "Please use a text-based PDF or run OCR (Optical Character Recognition) first."
        )
    else:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(raw_text)
        if not chunks:
            st.error("No text chunks found. Nothing to embed.")
        else:
            st.success(f"Loaded! Split into {len(chunks)} chunks.")
            vector_store = FAISS.from_texts(chunks, embedding=embeddings)
            qa = RetrievalQA.from_chain_type(
                llm = llm ,
                chain_type="stuff",
                retriever=vector_store.as_retriever(),
                )
            query = st.text_input("Ask a question about your PDF:")
            if query:
                with st.spinner("Thinking..."):
                    answer = qa.run(query)
                st.subheader("Answer")
                st.write(answer)

"""
#rag chat bot with fiass ,groq
import streamlit as st
from PyPDF2 import PdfReader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Streamlit UI
st.set_page_config(page_title="RAG PDF Chatbot", layout="centered")
st.title("📄 RAG App: Ask Your PDF Anything")

# Upload PDF
uploaded_file = st.file_uploader(
    "Upload your PDF document",
    type=["pdf"]
)

if uploaded_file is not None:
    raw_text = ""

    try:
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                raw_text += text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")

    if not raw_text.strip():
        st.error(
            "❌ No text found in PDF.\n\n"
            "This may be a scanned image PDF.\n"
            "Please upload a text-based PDF."
        )
    else:
        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = text_splitter.split_text(raw_text)
        st.success(f"✅ Loaded! Split into {len(chunks)} chunks.")

        # Embeddings (FREE, local)
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Vector store
        vector_store = FAISS.from_texts(chunks, embedding=embeddings)

        # Groq LLM
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0
        )

        # RAG Chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever()
        )

        # Ask question
        query = st.text_input("❓ Ask a question about your PDF")

        if query:
            with st.spinner("Thinking... 🤔"):
                answer = qa_chain.run(query)

            st.subheader("📌 Answer")
            st.write(answer)
