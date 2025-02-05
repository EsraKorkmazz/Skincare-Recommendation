import os
import streamlit as st
import pandas as pd
import requests
import time
from typing import Optional

class SummaryGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.base_url = "https://api-inference.huggingface.co/models/t5-small"
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def get_summary(self, review_text: str) -> Optional[str]:
        if not review_text or len(review_text.strip()) == 0:
            return "No review text available"

        for attempt in range(self.max_retries):
            try:
                # Truncate long reviews to prevent API issues
                truncated_review = review_text[:1000] + "..." if len(review_text) > 1000 else review_text
                
                # Construct a clear prompt for the model
                prompt = f"summarize: {truncated_review}"
                
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json={"inputs": prompt},
                    timeout=10  # Add timeout
                )
                
                if response.status_code == 429:  # Rate limit
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
                response.raise_for_status()
                
                summary_data = response.json()
                if isinstance(summary_data, list) and len(summary_data) > 0:
                    return summary_data[0]['generated_text']
                else:
                    st.warning(f"Unexpected API response format: {summary_data}")
                    return "Summary unavailable"
                    
            except requests.exceptions.Timeout:
                st.warning(f"Request timed out (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
            except requests.exceptions.RequestException as e:
                st.error(f"API request failed: {str(e)}")
                return "Summary generation failed due to API error"
            except Exception as e:
                st.error(f"Unexpected error during summary generation: {str(e)}")
                return "Summary generation failed"
        
        return "Summary generation failed after retries"

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
        self.summary_generator = SummaryGenerator(st.secrets["skin"]["HF_API_KEY"])

    def _generate_summaries(self, products_df: pd.DataFrame) -> list:
        summaries = []
        for review in products_df['Reviews']:
            with st.spinner("Generating product summary..."):
                summary = self.summary_generator.get_summary(review)
                summaries.append(summary)
            # Add small delay between API calls to avoid rate limiting
            time.sleep(0.5)
        return summaries

    def get_content_based_recommendations(self, product_name: str, skin_type: str, scent: str, top_n: int = 20):
        try:
            mask = self.data['Skin Type Compatibility'].str.contains(skin_type, case=False, na=False)
            if scent != 'All':
                mask &= self.data['Scent'].str.contains(scent, case=False, na=False)
            
            filtered_data = self.data[mask].drop_duplicates(subset=['Product Name'])
            
            if filtered_data.empty:
                st.warning("No products found matching your criteria.")
                return [], [], [], [], [], []
            
            recommended_products = filtered_data.head(top_n)
            summaries = self._generate_summaries(recommended_products)
            
            return (
                recommended_products['Product Name'].tolist(),
                recommended_products['Product Brand'].tolist(),
                recommended_products['Image Link'].tolist(),
                recommended_products['Product Link'].tolist(),
                recommended_products['Ease of Use'].tolist(),
                summaries
            )
            
        except Exception as e:
            st.error(f"Error in recommendation generation: {str(e)}")
            return [], [], [], [], [], []

    def get_product_based_recommendations(self, selected_product: str, top_n: int = 20):
        try:
            if selected_product not in self.data['Product Name'].values:
                st.warning("Selected product not found in database.")
                return [], [], [], [], [], []
            
            recommended_products = self.data.head(top_n)
            recommended_products = recommended_products.drop_duplicates(subset='Product Name')
            summaries = self._generate_summaries(recommended_products)
            
            return (
                recommended_products['Product Name'].tolist(),
                recommended_products['Product Brand'].tolist(),
                recommended_products['Image Link'].tolist(),
                recommended_products['Product Link'].tolist(),
                recommended_products['Ease of Use'].tolist(),
                summaries
            )
            
        except Exception as e:
            st.error(f"Error in product-based recommendation: {str(e)}")
            return [], [], [], [], [], []