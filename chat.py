import openai
import streamlit as st

OPENAI_API_KEY = st.secrets["openai"]["openai_api_key"]
openai.api_key = OPENAI_API_KEY

def get_skin_recommendations(query):
    """Get skin care product recommendations using the OpenAI API"""
    prompt = f"List 10 skin care products that match these criteria: {query}. Just list the product names, one per line, without any additional text or numbering."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            max_tokens=150,
            messages=[
                {"role": "system", "content": "You are a skin care expert. Provide only skin care product names based on the user's criteria without any additional text."},
                {"role": "user", "content": prompt}
            ]
        )
        
        product_recommendations = response['choices'][0]['message']['content'].strip().split('\n')
        
        return product_recommendations
    
    except Exception as e:
        st.error(f"OpenAI API error: {str(e)}")
        return None
