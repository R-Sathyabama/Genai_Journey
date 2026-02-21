import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()
# Initialize LLM
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",
    temperature=0.3
)
# Prompt to generate Q&A pairs
qa_prompt = ChatPromptTemplate.from_template(
"""
You are a senior technical interviewer.
Given this Job Role: {role}
And this Job Description: {jd}

Generate 5 **technical** mock interview questions for this role.
Only include questions that test technical skills, knowledge, or problem-solving.
Do NOT include situational or behavioral questions.

For each question, also provide a clear, strong sample answer.
Number them 1 to 5, and format like this:
1. Question: ...
   Answer:...
"""
)
# Create chain
qa_chain = qa_prompt | llm
# Streamlit UI
st.title("Mock Interview Practice")
role = st.text_input("Job Role (e.g., Data Analyst)")
jd = st.text_area("Job Description (paste here):")
if st.button("Generate Q&A"):
    if not role or not jd:
        st.warning("Please enter both the Role and JD.")
    else:
        qa_pairs = qa_chain.invoke({"role": role, "jd": jd})
        st.subheader("Mock Interview Q&A")
        st.write(qa_pairs.content)