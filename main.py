import streamlit as st
import pandas as pd
from recommendation_model import RecommendationEngine
from streamlit_option_menu import option_menu
st.set_page_config(layout="wide")

if 'recommendation_batch' not in st.session_state:
    st.session_state.recommendation_batch = 0
    st.session_state.total_recommendations = []

def load_recommendation_engine(data_path):
    return RecommendationEngine(data_path)

data_path = "data/final_data_cleaned.csv"
recommendation_engine = RecommendationEngine(data_path)

data = pd.read_csv(data_path)
data.fillna("", inplace=True)

selected = option_menu(
    menu_title=None,
    options=["Home", "Recommendation","Product Based Recommendation", "About"],
    icons=["house", "magic", "magic", "info-circle"], 
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "5px", "background": "linear-gradient(to right, #ff69b4, #ffd700)"},
        "icon": {
            "color": "white", 
            "font-size": "25px", 
            "transition": "transform 0.3s ease-in-out"  
        },
        "nav-link": {
            "font-size": "23px", 
            "color" : "white",
            "text-align": "middle", 
            "margin": "15px",  
            "border-radius": "8px",
        },
        "nav-link-selected": {
            "background-color": "#ffb6c1", 
            "color": "white" 
        },
        "icon:hover": {
            "transform": "rotate(360deg)", 
            "color": "#ff9800" 
        }
    }
)

if selected == "Home":
    st.title("Welcome to Skin Pro! Your Personalized Skincare Assistant.")
    st.write("### Discover the perfect skincare routine tailored just for you. Whether you're dealing with acne, dryness, aging, or simply want to glow, SKIN PRO provides expert-backed, customized product recommendations to help you achieve your skin goals.")
    st.header("Key Features")

    st.markdown("""
    - **Tailored Skin Care Routine**: Receive personalized recommendations based on your specific skin concerns and goals.
    - **Skin Type Analysis**: Identify your skin type and get expert advice on the best products suited for your skin.
    - **Product Reviews & Ratings**: Explore what other users are saying about the products we recommend. Find out which ones work best for your skin.
    - **Expert-backed Guidance**: Benefit from advice that combines scientific knowledge, dermatological research, and real user experiences.
    """)

    st.image("images/3.jpg", width=1000)
    st.write("### While my skincare recommendation engine helps match you with the right products, this section is dedicated to sharing practical skincare tips. From building a morning routine to evening care, these tips are designed to help you achieve healthy, glowing skin.")
    st.image("images/2.png", width=1000)
    st.write("### Let’s dive into the essentials of skincare!")

elif selected == "Recommendation":
    st.title("Skincare Product Recommendation")
    st.write("Please select your preferences to get personalized skincare product recommendations.")
    
    st.write("1. Select your skin type from the dropdown menu.")
    st.write("2. Choose your scent preference.")
    st.write("4. Click the 'Get Recommendations' button to see the recommended products.")

    skin_type = st.selectbox("Select Your Skin Type", ['Oily', 'Dry', 'Sensitive', 'Combination', 'Normal', 'Acne', 'Aging', 'All'])
    scent = st.selectbox("Select scent preference", ['Light', 'Strong', 'All'])
        
    if st.button("Get Recommendations :sparkles:"):
        st.session_state.recommendation_batch = 0
        st.session_state.total_recommendations = []

        with st.spinner("Fetching recommendations..."):
            filtered_products = data[
                (data['Skin Type Compatibility'].str.contains(skin_type, case=False, na=False)) &
                (data['Scent'].str.contains(scent, case=False, na=False) | (scent == 'All'))
            ]
            if filtered_products.empty:
                st.warning("No products found matching your criteria. Please try different preferences.")
            else:
                sample_product = filtered_products.iloc[0]['Product Name']
                recommended_names, recommended_brands, recommended_images, recommended_links, recommended_ease_of_use, recommended_summaries = recommendation_engine.get_content_based_recommendations(sample_product, skin_type, scent, top_n=40)
                
                st.session_state.total_recommendations = list(zip(
                    recommended_names, 
                    recommended_brands, 
                    recommended_images, 
                    recommended_links, 
                    recommended_ease_of_use, 
                    recommended_summaries
                ))

    if st.session_state.total_recommendations:
        BATCH_SIZE = 3
        current_batch = st.session_state.total_recommendations[
            st.session_state.recommendation_batch:st.session_state.recommendation_batch + BATCH_SIZE
        ]

        cols = st.columns(min(BATCH_SIZE, len(current_batch)))
        
        for j, col in enumerate(cols):
            if j < len(current_batch):
                with col:
                    name, brand, image, link, ease_of_use, summary = current_batch[j]
                    st.markdown(f"**{brand}**")
                    st.image(image, 
                        caption=name, 
                        use_container_width=True)
                    with st.expander("What customers say about this product"):
                        st.write(f"Ease of Use: {ease_of_use}")
                        st.write(f"Summary: {summary}")
                        st.write(f"[View Product]({link})")

        if st.session_state.recommendation_batch + BATCH_SIZE < len(st.session_state.total_recommendations):
            if st.button("Load More Recommendations"):
                st.session_state.recommendation_batch += BATCH_SIZE
                st.experimental_rerun()

elif selected == "Product Based Recommendation":
    st.title("Product Based Recommendation")
    st.write("Please select a product to get recommendations based on that product.")
    
    selected_product = st.selectbox("Select a product", data['Product Name'])
    
    if st.button("Get Recommendations :sparkles:"):
        st.session_state.recommendation_batch = 0
        st.session_state.total_recommendations = []

        with st.spinner("Fetching recommendations..."):
            recommended_names, recommended_brands, recommended_images, recommended_links, recommended_ease_of_use, recommended_summaries = recommendation_engine.get_product_based_recommendations(selected_product, top_n=20)
            
            if not recommended_names:
                st.warning("No recommendations found for this product.")
            else:
                st.session_state.total_recommendations = list(zip(
                    recommended_names, 
                    recommended_brands, 
                    recommended_images, 
                    recommended_links, 
                    recommended_ease_of_use, 
                    recommended_summaries
                ))

    if st.session_state.total_recommendations:
        BATCH_SIZE = 3
        current_batch = st.session_state.total_recommendations[
            st.session_state.recommendation_batch:st.session_state.recommendation_batch + BATCH_SIZE
        ]

        cols = st.columns(min(BATCH_SIZE, len(current_batch)))
        
        for j, col in enumerate(cols):
            if j < len(current_batch):
                with col:
                    name, brand, image, link, ease_of_use, summary = current_batch[j]
                    st.markdown(f"**{brand}**")
                    st.image(image, 
                        caption=name, 
                        use_container_width=True)
                    with st.expander("What customers say about this product"):
                        st.write(f"Ease of Use: {ease_of_use}")
                        st.write(f"Summary: {summary}")
                        st.write(f"[View Product]({link})")

        if st.session_state.recommendation_batch + BATCH_SIZE < len(st.session_state.total_recommendations):
            if st.button("Load More Recommendations"):
                st.session_state.recommendation_batch += BATCH_SIZE
                st.experimental_rerun()

elif selected == "About":
    st.write("For More Information\n" + "https://github.com/EsraKorkmazz/skincare-product-recommendation-engine")