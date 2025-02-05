import requests
import streamlit as st

api_key = st.secrets["skin"]["HF_API_KEY"]

headers = {"Authorization": f"Bearer {api_key}"}
model_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

def get_bot_response(user_input: str) -> str:
    data = {
        "inputs": user_input,
        "parameters": {"max_length": 50}
    }

    response = requests.post(model_url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()[0]['generated_text']
    else:
        return f"Error: {response.status_code}"

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    bot_response = get_bot_response(user_input)
    print(f"Bot: {bot_response}")
