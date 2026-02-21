"""
Excel-based RAG Chatbot
- Works with ANY Excel file
- Any number of columns
- Semantic search using HuggingFace embeddings
- Answers via Groq LLM
"""

# -----------------------------
# 1️⃣ Install dependencies (run once)
# -----------------------------
# pip install pandas openpyxl langchain langchain-community chromadb sentence-transformers langchain-groq transformers torch

# -----------------------------
# 2️⃣ Imports
# -----------------------------
import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_community.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSources

# -----------------------------
# 3️⃣ Load Excel
# -----------------------------
excel_path = "data.xlsx"  # Change to your Excel file
df = pd.read_excel(excel_path)

# -----------------------------
# 4️⃣ Convert all rows into text (any columns)
# -----------------------------
# Combine all column values per row into one string
texts = df.astype(str).agg(" | ".join, axis=1).tolist()

# -----------------------------
# 5️⃣ Create HuggingFace embeddings
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# 6️⃣ Store in Chroma DB
# -----------------------------
vectorstore = Chroma.from_texts(
    texts=texts,
    embedding=embeddings,
    persist_directory="excel_chroma_db"
)
vectorstore.persist()

# -----------------------------
# 7️⃣ Create Retriever
# -----------------------------
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# -----------------------------
# 8️⃣ Initialize Groq LLM
# -----------------------------
llm = ChatGroq(
    model="qwen/qwen3-32b",  # replace with your Groq-supported model
    temperature=0.0
)

# -----------------------------
# 9️⃣ Create RetrievalQA Chain
# -----------------------------
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff"
)

# -----------------------------
# 🔟 Interactive Chat
# -----------------------------
print("\nExcel RAG Chatbot Ready! Type 'exit' to stop.\n")

while True:
    query = input("Ask your question: ")
    if query.lower() == "exit":
        print("Goodbye!")
        break

    answer = qa_chain.run(query)
    print("\nAnswer:", answer, "\n")
