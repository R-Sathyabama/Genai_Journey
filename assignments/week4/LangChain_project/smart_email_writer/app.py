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

# Define the prompt template
prompt = PromptTemplate(
    input_variables=["bullet_points"],
    template="""
    You are an expert email writer. Using the following bullet points, draft a professional,
    {bullet_points}
    Make sure the email has a greeting, clear structure, and a closing.
    """
    )
# Create the chain
chain = prompt | llm
# Streamlit LIT
# Streamlit UI
st.title("Smart Email Writer")
st.write("Enter key bullet points for your email below:")
bullet_points = st.text_area("Bullet Points", height=200)
if st.button("Generate Email"):
    if bullet_points.strip() == "":
        st.warning("Please enter some bullet points.")
    else:
        email = chain.invoke({"bullet_points": bullet_points})
        st.subheader("Drafted Email")
        st.write(email.content)