import os
import streamlit as st
import pandas as pd
import requests
import time
from typing import Optional

api_key = st.secrets["skin"]["HF_API_KEY"]

class SummaryGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.base_url = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
        self.max_retries = 3
        self.retry_delay = 2 

    def get_summary(self, review_text: str) -> Optional[str]:
        if not review_text or len(review_text.strip()) == 0:
            return "No review text available"

        for attempt in range(self.max_retries):
            try:
                truncated_review = review_text[:500] + "..." if len(review_text) > 500 else review_text
                prompt = f"summarize: {truncated_review}"
                
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json={"inputs": prompt, "parameters": {"max_length": 100, "min_length": 30}},
                    timeout=10
                )
                
                if response.status_code == 429:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                
                if response.status_code == 401:
                    return self._get_review_excerpt(review_text)
                    
                response.raise_for_status()
                
                summary_data = response.json()
                if isinstance(summary_data, list) and len(summary_data) > 0:
                    return str(summary_data[0]['generated_text'])
                else:
                    return self._get_review_excerpt(review_text)
                    
            except Exception as e:
                if attempt == self.max_retries - 1: 
                    return self._get_review_excerpt(review_text)
                time.sleep(self.retry_delay)
                
        return self._get_review_excerpt(review_text)

    def _get_review_excerpt(self, review: str, max_length: int = 200) -> str:
        """Fallback method to create a brief excerpt from the review text"""
        if not review or len(review.strip()) == 0:
            return "No review available"
        
        excerpt = review[:max_length]
        last_period = excerpt.rfind('.')
        if last_period > 0:
            excerpt = excerpt[:last_period + 1]
        return excerpt.strip()

class RecommendationEngine:
    def __init__(self, data_path: str):
        self.data = pd.read_csv(data_path)
        self.data['Combined Text'] = (
            self.data['Reviews'] + " " +
            self.data['Skin Type Compatibility'] + " " +
            self.data['Product Name'] + " " +
            self.data['Product Brand'] + " " +
            self.data['Scent'] + " " +
            self.data['Effectiveness']
        )
        self.data.fillna("", inplace=True)
        
        try:
            self.summary_generator = SummaryGenerator(st.secrets["skin"]["HF_API_KEY"])
        except:
            st.warning("API key not found or invalid. Using review excerpts instead.")
            self.summary_generator = None

    def _process_reviews(self, products_df: pd.DataFrame) -> list:
        """Process reviews with fallback to excerpts if API fails"""
        processed_reviews = []
        for review in products_df['Reviews']:
            if self.summary_generator:
                try:
                    summary = self.summary_generator.get_summary(review)
                    processed_reviews.append(summary)
                except:
                    processed_reviews.append(self.summary_generator._get_review_excerpt(review))
            else:
                processed_reviews.append(self.summary_generator._get_review_excerpt(review))
        return processed_reviews

    def get_content_based_recommendations(self, product_name, skin_type, scent, top_n=20):
        try:
            mask = self.data['Skin Type Compatibility'].str.contains(skin_type, case=False, na=False)
            if scent != 'All':
                mask &= self.data['Scent'].str.contains(scent, case=False, na=False)
            
            filtered_data = self.data[mask].drop_duplicates(subset=['Product Name'])
            
            if filtered_data.empty:
                return [], [], [], [], [], []
            
            idx = (filtered_data.index[0] if product_name not in filtered_data['Product Name'].values
                   else self.data[self.data['Product Name'] == product_name].index[0])
            
            recommended_products = filtered_data.head(top_n)
            processed_reviews = self._process_reviews(recommended_products)
            
            return (
                recommended_products['Product Name'].tolist(),
                recommended_products['Product Brand'].tolist(),
                recommended_products['Image Link'].tolist(),
                recommended_products['Product Link'].tolist(),
                recommended_products['Ease of Use'].tolist(),
                processed_reviews
            )
            
        except Exception as e:
            st.error(f"Error in recommendation generation: {str(e)}")
            return [], [], [], [], [], []

    def get_product_based_recommendations(self, selected_product: str, top_n: int = 20):
        try:
            if selected_product not in self.data['Product Name'].values:
                return [], [], [], [], [], []
            
            recommended_products = self.data.head(top_n)
            recommended_products = recommended_products.drop_duplicates(subset='Product Name')
            processed_reviews = self._process_reviews(recommended_products)
            
            return (
                recommended_products['Product Name'].tolist(),
                recommended_products['Product Brand'].tolist(),
                recommended_products['Image Link'].tolist(),
                recommended_products['Product Link'].tolist(),
                recommended_products['Ease of Use'].tolist(),
                processed_reviews
            )
            
        except Exception as e:
            st.error(f"Error in product-based recommendation: {str(e)}")
            return [], [], [], [], [], []     