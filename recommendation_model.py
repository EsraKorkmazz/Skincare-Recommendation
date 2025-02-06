import os
import pandas as pd
import requests
import time
from typing import Optional
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

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
        except Exception as e:
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
                except Exception as e:
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
            
            filtered_data = filtered_data.reset_index(drop=True)

            if product_name in filtered_data['Product Name'].values:
                idx = filtered_data[filtered_data['Product Name'] == product_name].index[0]
            else:
                idx = 0

            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(filtered_data['Combined Text'])

            cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = [s for s in sim_scores if s[0] != idx]
            sim_scores = sim_scores[:top_n]
            product_indices = [i[0] for i in sim_scores]
            
            recommended_products = filtered_data.iloc[product_indices]
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
            # Ensure the selected product is in the dataset
            if selected_product not in self.data['Product Name'].values:
                return [], [], [], [], [], []

            # Get the index of the selected product in the dataset
            selected_product_idx = self.data[self.data['Product Name'] == selected_product].index[0]

            # Compute the similarity between the selected product and all other products in the dataset
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(self.data['Combined Text'])
            
            cosine_sim = linear_kernel(tfidf_matrix[selected_product_idx:selected_product_idx+1], tfidf_matrix).flatten()

            # Get the top N most similar products (excluding the selected product)
            sim_scores = list(enumerate(cosine_sim))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = [s for s in sim_scores if s[0] != selected_product_idx]
            sim_scores = sim_scores[:top_n]

            product_indices = [i[0] for i in sim_scores]

            # Filter the recommended products based on the indices
            recommended_products = self.data.iloc[product_indices]

            # Process reviews and return relevant product data
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

