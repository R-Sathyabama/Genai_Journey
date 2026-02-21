import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import PyPDF2

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",
    temperature=0.3
)

# Prompt for cover letter generation (CHAT prompt)
cover_letter_prompt = ChatPromptTemplate.from_template("""
You are an expert career coach and writer.

Write a professional, personalized cover letter for this role:

Job Title: {job_title}
Company: {company}

Use the following resume information:
{resume_text}

Keep the tone formal but friendly. Highlight relevant experience and enthusiasm for the role.
"""
)

# ✅ Correct chain order
cover_letter_chain = cover_letter_prompt | llm

# Streamlit UI
st.title("Cover Letter Generator")

uploaded_file = st.file_uploader(
    "Upload your Resume (PDF or TXT)",
    type=["pdf", "txt"]
)

job_title = st.text_input("Job Title (e.g., Software Engineer)")
company = st.text_input("Company Name (optional)")

if st.button("Generate Cover Letter"):
    if not uploaded_file or not job_title:
        st.warning("Please upload your resume and enter the job title.")
    else:
        # Extract resume text
        if uploaded_file.name.endswith(".txt"):
            resume_text = uploaded_file.read().decode("utf-8")

        elif uploaded_file.name.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            resume_text = ""
            for page in pdf_reader.pages:
                resume_text += page.extract_text() or ""

        else:
            st.error("Unsupported file type.")
            resume_text = ""

        if resume_text:
            result = cover_letter_chain.invoke({
                "resume_text": resume_text,
                "job_title": job_title,
                "company": company if company else "the company"
            })

            st.subheader("Generated Cover Letter")
            st.write(result.content)
