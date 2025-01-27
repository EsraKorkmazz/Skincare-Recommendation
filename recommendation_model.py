import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
import pandas as pd
from sklearn.decomposition import TruncatedSVD

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
        self.cosine_sim = self.create_tfidf_matrix(self.data)
        self.summarizer = self.load_summarizer()
    
    @st.cache_resource
    def load_summarizer(self):
        return pipeline("summarization", model="facebook/bart-base", device=-1)

    def create_tfidf_matrix(self, _data):
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(_data['Combined Text'])
        svd = TruncatedSVD(n_components=100)
        reduced_matrix = svd.fit_transform(tfidf_matrix)
        return cosine_similarity(reduced_matrix, reduced_matrix)

    def get_review_summary(self, review_text, max_length=128):
        if len(review_text) > 1000:
            review_text = review_text[:1000]
        try:
            summary = self.summarizer(
                review_text,
                max_length=max_length,
                min_length=30,
                do_sample=False
            )
            return summary[0]['summary_text']
        except Exception:
            return "Summary generation failed."

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
            sim_scores = [(i, self.cosine_sim[idx][i]) for i in filtered_data.index]
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[:top_n]
            product_indices = [i[0] for i in sim_scores]

            recommended_products = self.data.iloc[product_indices]

            summaries = [self.get_review_summary(review) for review in recommended_products['Reviews']]

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

            idx = self.data[self.data['Product Name'] == selected_product].index[0]
            sim_scores = [(i, self.cosine_sim[idx][i]) for i in range(len(self.data))]
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[:top_n]
            product_indices = [i[0] for i in sim_scores]

            recommended_products = self.data.iloc[product_indices]

            summaries = [self.get_review_summary(review) for review in recommended_products['Reviews']]

            return (recommended_products['Product Name'].tolist(),
                    recommended_products['Product Brand'].tolist(),
                    recommended_products['Image Link'].tolist(),
                    recommended_products['Product Link'].tolist(),
                    recommended_products['Ease of Use'].tolist(),
                    summaries)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return [], [], [], [], [], []

    
    