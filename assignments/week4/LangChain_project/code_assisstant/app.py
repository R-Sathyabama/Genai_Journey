import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

import os
from dotenv import load_dotenv
load_dotenv()
# Initialize the LLM
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # ASCII letters
    model_name="gpt-4o-mini",
    temperature=0.5
    )
# Define the prompt
prompt = PromptTemplate(
    input_variables=["code_task"],
    template="""
    You are a professional coding assistant. Help the user with the following task:
    {code_task}
    Provide clean, well-commented code and explanations if needed.
    """
)
# Create the chain
chain = prompt | llm
# Streamlit UI
st.title("Code Assistant")
code_task = st.text_area("Describe your coding task:")
if st.button("Generate Code"):
    if code_task.strip() == "":
        st.warning("Please enter a task description.")
    else:
        response = chain.invoke({"code_task": code_task})
        st.subheader("Assistant Response")
        st.code(response, language='python')