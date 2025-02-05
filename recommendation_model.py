import os
import streamlit as st
import pandas as pd
import requests
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")

HF_API_KEY = st.secrets["skin"]["HF_API_KEY"]

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

def get_summary_from_api(review_text):
    try:
        url = "https://api-inference.huggingface.co/models/t5-small"
        data = {"inputs": review_text}
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status() 
        summary = response.json()[0]['generated_text']
        return summary
    except Exception as e:
        return "Summary generation failed."

class RecommendationEngine:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        self.data['Combined Text'] = (self.data['Reviews'] + " " +
                                      self.data['Skin Type Compatibility'] + " " +
                                      self.data['Product Name'] + " " +
                                      self.data['Product Brand'] + " " +
                                      self.data['Scent'] + " " +
                                      self.data['Effectiveness'])
        self.data.fillna("", inplace=True)
    
    def get_content_based_recommendations(self, product_name, skin_type, scent, top_n=20):
        try:
            mask = self.data['Skin Type Compatibility'].str.contains(skin_type, case=False, na=False)
            if scent != 'All':
                mask &= self.data['Scent'].str.contains(scent, case=False, na=False)
            filtered_data = self.data[mask].drop_duplicates(subset=['Product Name'])

            if filtered_data.empty:
                return [], [], [], [], [], []

            recommended_products = filtered_data.head(top_n)
            summaries = [get_summary_from_api(review) for review in recommended_products['Reviews']]

            return (recommended_products['Product Name'].tolist(),
                    recommended_products['Product Brand'].tolist(),
                    recommended_products['Image Link'].tolist(),
                    recommended_products['Product Link'].tolist(),
                    recommended_products['Ease of Use'].tolist(),
                    summaries)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return [], [], [], [], [], []

    def get_product_based_recommendations(self, selected_product, top_n=20):
        try:
            if selected_product not in self.data['Product Name'].values:
                return [], [], [], [], [], []

            recommended_products = self.data.head(top_n) 
            recommended_products = recommended_products.drop_duplicates(subset='Product Name')
            summaries = [get_summary_from_api(review) for review in recommended_products['Reviews']]

            return (recommended_products['Product Name'].tolist(),
                    recommended_products['Product Brand'].tolist(),
                    recommended_products['Image Link'].tolist(),
                    recommended_products['Product Link'].tolist(),
                    recommended_products['Ease of Use'].tolist(),
                    summaries)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return [], [], [], [], [], []

