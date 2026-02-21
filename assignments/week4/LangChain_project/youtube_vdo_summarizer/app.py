import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
)

# Prompt template for summarization
summary_prompt = ChatPromptTemplate.from_template(
"""
You are an expert summarizer.
Here is a video transcript:
{transcript}
Please generate a clear, concise summary of the main points and topics.
"""
)

# Create the chain
summary_chain = summary_prompt | llm

# Streamlit UI
st.title("YouTube Video Summarizer")
video_url = st.text_input("Enter YouTube Video URL:")

def get_video_id(url):
    """
    Extract video ID from a YouTube URL
    """
    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    elif parsed_url.hostname in ("www.youtube.com", "youtube.com"):
        query = parse_qs(parsed_url.query)
        return query.get("v", [None])[0]
    return None

if st.button("Summarize"):
    if not video_url:
        st.warning("Please enter a video URL.")
    else:
        video_id = get_video_id(video_url)
        if not video_id:
            st.error("Invalid YouTube URL.")
        else:
            try:
                # --- Fetch transcript for v1.2.4 ---
                transcript_list = YouTubeTranscriptApi.fetch_transcript(video_id)
                full_text = " ".join([t['text'] for t in transcript_list])

                if not full_text.strip():
                    st.warning("Transcript is empty or unavailable.")
                else:
                    # Generate summary
                    summary = summary_chain.invoke({"transcript": full_text})
                    st.subheader("Video Summary")
                    st.text_area("Summary", summary.content, height=300)

            except Exception as e:
                st.error(f"Error fetching transcript or generating summary: {str(e)}")
                st.info("Tip: Make sure the video has captions enabled and the URL is correct.")
