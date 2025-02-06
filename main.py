import streamlit as st
import pandas as pd
from recommendation_model import RecommendationEngine
from streamlit_option_menu import option_menu
from chat import get_skin_recommendations
from nltk.sentiment import SentimentIntensityAnalyzer

st.set_page_config(layout="wide")
api_key = st.secrets["skin"]["HF_API_KEY"]

@st.cache_data
def load_data():
    data_path = "data/final_data_cleaned.csv"
    data = pd.read_csv(data_path)
    data.fillna("", inplace=True)
    return data, data_path

data, data_path = load_data()
recommendation_engine = RecommendationEngine(data_path)

selected = option_menu(
    menu_title=None,
    options=["Home","Popular Products", "Recommendation", "Product Based Recommendation", "ChatBot", "About"],
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
            "color": "white",
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
    st.image("images/3.jpg", use_container_width=True)
    st.write("### While my skincare recommendation engine helps match you with the right products, this section is dedicated to sharing practical skincare tips. From building a morning routine to evening care, these tips are designed to help you achieve healthy, glowing skin.")
    st.image("images/2.png", use_container_width=True)
    st.write("### Let's dive into the essentials of skincare!")

elif selected == "Popular Products":
    try:
        ulta_data = pd.read_csv("data/final_data_cleaned.csv")
        top_10_products = pd.read_csv("top_20_products.csv")

        st.title("Top 20 Most Popular and Loved Products")
        st.write("""
        Based on user reviews and sentiment analysis, here are the top 20 products that have received the most love from our customers!
        """)
        num_columns = 3  
        columns = st.columns(num_columns)
        for idx, row in top_10_products.iterrows():
            column_idx = idx % num_columns 
            with columns[column_idx]:
                st.markdown(f"<h3 style='text-align: center; font-weight: bold;'>{row['Product Name']}</h3>", unsafe_allow_html=True)

                product_image = row.get('Image Link', 'default_image.jpg')
                product_link = row.get('Product Link', '#')

                st.image(product_image, use_container_width=True)
                st.markdown(f"[View Product]({product_link})", unsafe_allow_html=True)
                st.write("---")

    except Exception as e:
        st.error(f"Error in displaying popular products: {str(e)}")

elif selected == "Recommendation":
    st.title("Skincare Product Recommendation")
    st.write("Please select your preferences to get personalized skincare product recommendations.")
    st.write("1. Select your skin type from the dropdown menu.")
    st.write("2. Choose your scent preference.")
    st.write("3. Click the 'Get Recommendations' button to see the recommended products.")

    skin_type = st.selectbox("Select Your Skin Type", ['Oily', 'Dry', 'Sensitive', 'Combination', 'Normal', 'Acne', 'Aging','Eczema', 'All'])
    scent = st.selectbox("Select scent preference", ['Light', 'Strong', 'All'])

    if st.button("Get Recommendations :sparkles:"):
        with st.spinner("Finding the perfect products for you..."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Getting initial recommendations...")
            progress_bar.progress(25)

            filtered_products = data[
                (data['Skin Type Compatibility'].str.contains(skin_type, case=False, na=False)) &
                (data['Scent'].str.contains(scent, case=False, na=False) | (scent == 'All'))
            ]

            if filtered_products.empty:
                st.warning("No products found matching your criteria. Please try different preferences.")
            else:
                sample_product = filtered_products.iloc[0]['Product Name']
                recommended_products = recommendation_engine.get_content_based_recommendations(
                    sample_product, skin_type, scent, top_n=43
                )
                if not any(recommended_products):
                    st.warning("No recommendations found. Please try different preferences.")
                else:
                    progress_bar.progress(75)
                    status_text.text("Preparing your personalized recommendations...")

                    names, brands, images, links, ease_of_use, summaries = recommended_products

                    BATCH_SIZE = 3
                    for i in range(0, len(names), BATCH_SIZE):
                        cols = st.columns(min(BATCH_SIZE, len(names) - i))
                        for j, col in enumerate(cols):
                            idx = i + j
                            if idx < len(names):
                                with col:
                                    st.markdown(f"### {brands[idx]}")
                                    st.image(images[idx], caption=names[idx], use_container_width=True)
                                    with st.expander("Product Details"):
                                        st.write(f"**Ease of Use:** {ease_of_use[idx]}")
                                        st.write("**Product Summary:**")
                                        st.write(summaries[idx])
                                        st.markdown(f"[View Product]({links[idx]})")
                
                progress_bar.progress(100)
                status_text.empty()

elif selected == "Product Based Recommendation":
    st.title("Product Based Recommendation")
    st.write("Please select a product to get recommendations based on that product.")
    
    selected_product = st.selectbox(
        "Select a product",
        options=data['Product Name'].unique(),
        help="Choose a product you like to find similar products"
    )
    
    if st.button("Get Recommendations :sparkles:"):
        with st.spinner("Finding similar products..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            progress_bar.progress(25)
            recommended_products = recommendation_engine.get_product_based_recommendations(
                selected_product,
                top_n=43
            )
            
            if not any(recommended_products):
                st.warning("No recommendations found for this product.")
            else:
                status_text.text("Preparing your recommendations...")
                progress_bar.progress(75)
                
                names, brands, images, links, ease_of_use, summaries = recommended_products

                BATCH_SIZE = 3
                for i in range(0, len(names), BATCH_SIZE):
                    cols = st.columns(min(BATCH_SIZE, len(names) - i))
                    for j, col in enumerate(cols):
                        idx = i + j
                        if idx < len(names):
                            with col:
                                st.markdown(f"### {brands[idx]}")
                                st.image(images[idx], caption=names[idx], use_container_width=True)
                                with st.expander("Product Details"):
                                    st.write(f"**Ease of Use:** {ease_of_use[idx]}")
                                    st.write("**Product Summary:**")
                                    st.write(summaries[idx])
                                    st.markdown(f"[View Product]({links[idx]})")
            
            progress_bar.progress(100)
            status_text.empty()

elif selected == "ChatBot":
    query = st.text_input("Enter your skin care needs (e.g., 'products for dry skin with anti-aging properties')")

    if query:
        with st.spinner("Fetching skin care product recommendations..."):
            recommendations = get_skin_recommendations(query)
        
        if recommendations:
            st.write("Here are some skin care product recommendations based on your needs:")
            for product in recommendations:
                st.write(f"- {product}")
        else:
            st.warning("No recommendations found.")


elif selected == "About":
    st.title("About Skin Pro")
    st.write("""
    Skin Pro is a personalized skincare recommendation system designed to help you find the perfect products for your skin type and concerns.
    
    For more information and to view the source code, visit:
    https://github.com/EsraKorkmazz/skincare-product-recommendation-engine
    
    Created with ❤️ by Esra Korkmaz
    """)
