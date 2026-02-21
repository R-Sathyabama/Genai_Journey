import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

# ================= ENV =================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ================= LLM =================
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)

embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# ================= UI =================
st.set_page_config(page_title="Corrective RAG Excel Chatbot")
st.title("📊 Corrective RAG – Excel Chatbot")

uploaded_file = st.file_uploader(
    "Upload Excel / CSV file",
    type=["csv", "xlsx"]
)

# ================= LOAD EXCEL =================
def load_excel(file):
    if file.name.endswith(".csv"):
        try:
            return pd.read_csv(file, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(file, encoding="latin-1")
    else:
        return pd.read_excel(file)

# ================= VECTOR STORE =================
@st.cache_resource
def build_vectorstore(df):
    rows = df.astype(str).apply(lambda x: " | ".join(x), axis=1).tolist()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    docs = splitter.create_documents(rows)

    vectordb = Chroma.from_documents(
        docs,
        embedding=embeddings,
        persist_directory="./chroma_excel"
    )
    return vectordb

# ================= STEP 1: CONTEXT EVALUATION =================
EVAL_PROMPT = PromptTemplate(
    input_variables=["query", "context"],
    template="""
You are a Corrective RAG evaluator.

Query:
{query}

Retrieved Context:
{context}

Evaluate the context strictly.

Scores (0-1):
1. Relevance Score:
2. Completeness Score:
3. Accuracy Score:
4. Specificity Score:

Overall Quality:
Choose ONLY one → Excellent / Good / Fair / Poor

Respond EXACTLY in this format:
Relevance:
Completeness:
Accuracy:
Specificity:
Overall:
"""
)

# ================= STEP 3: ANSWER GENERATION =================
ANSWER_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are answering using ONLY the Excel data below.
Perform comparisons and numeric reasoning if required.
Do NOT say "not available" if values exist.

Excel Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""
)

# ================= CORRECTIVE RAG PIPELINE =================
def corrective_rag(query, vectordb):
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})
    docs = retriever.get_relevant_documents(query)
    context = "\n".join(d.page_content for d in docs)

    # ---- Step 1: Evaluate Context ----
    eval_output = llm.invoke(
        EVAL_PROMPT.format(query=query, context=context)
    ).content

    overall_quality = "Poor"
    for line in eval_output.splitlines():
        if line.startswith("Overall"):
            overall_quality = line.split(":")[1].strip()

    # ---- Step 2: Correction Decision ----
    if overall_quality in ["Poor", "Fair"]:
        action = "Retrieve_again"
        confidence = "Medium"

        refined_query = f"{query} including all relevant rows and numeric comparisons"
        retriever = vectordb.as_retriever(search_kwargs={"k": 8})
        docs = retriever.get_relevant_documents(refined_query)
        context = "\n".join(d.page_content for d in docs)

    else:
        action = "PROCEED_WITH_ANSWER"
        confidence = "High"

    # ---- Step 3: Response Generation ----
    answer = llm.invoke(
        ANSWER_PROMPT.format(context=context, question=query)
    ).content

    return {
        "quality": overall_quality,
        "confidence": confidence,
        "answer": answer,
        "action": action
    }

# ================= STREAMLIT FLOW =================
if uploaded_file:
    df = load_excel(uploaded_file)
    st.success("Excel loaded successfully")
    st.dataframe(df)

    vectordb = build_vectorstore(df)

    query = st.text_input("Ask a question from Excel")

    if query:
        with st.spinner("Running Corrective RAG..."):
            result = corrective_rag(query, vectordb)

        st.markdown("### 📌 Response")
        st.write(result["answer"])


