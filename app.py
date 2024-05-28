import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re

load_dotenv()  # Load all the environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

# Function to extract video ID from YouTube URL
def extract_video_id(url):
    regex_patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)",  # Regular YouTube URL
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^&]+)"               # Shortened YouTube URL
    ]
    for pattern in regex_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# Getting the transcript data from YouTube videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
        return transcript
    except Exception as e:
        raise e

# Getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

st.title("🎬 YouTube Transcript Summarizer")

youtube_link = st.text_input("Enter YouTube Video Link:")

# Button to get detailed notes
if st.button("🔍 Get Detailed Notes"):
    if youtube_link:
        with st.spinner("Analyzing the transcript... This may take a moment."):
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                summary = generate_gemini_content(transcript_text, prompt)
                st.markdown("## 📝 Detailed Notes:")
                st.write(summary)

                # Add a download button
                download_button_str = f"Download Summary as Text"
                download_filename = f"summary.txt"
                st.download_button(label=download_button_str, data=summary, file_name=download_filename)

# Display the thumbnail below the button
if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    else:
        st.error("Invalid YouTube URL. Please enter a valid URL.")