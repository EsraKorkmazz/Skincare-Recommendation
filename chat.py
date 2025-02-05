import asyncio
import aiohttp
import streamlit as st
from openai import OpenAI

TMDB_API_KEY = st.secrets["tmdb"]["TMDB_API_KEY"]
TMDB_BASE_URL = "https://api.themoviedb.org/3"

OPENAI_API_KEY = st.secrets["openai"]["api_key"]
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)

def get_movie_recommendations(query):
    """OpenAI API kullanarak cilt önerileri al"""
    prompt = f"List 10 movies that match these criteria: {query}. Just list the movie titles, one per line, without any additional text or numbering."
    
    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a movie recommendation expert. Provide only movie titles without any additional text."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI API error: {str(e)}")
        return None