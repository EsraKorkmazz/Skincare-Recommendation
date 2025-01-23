import streamlit as st
import pandas as pd
from recommendation_model import RecommendationEngine
from streamlit_option_menu import option_menu
st.set_page_config(layout="wide")

data_path = "/ulta2/recommendation-system/data/final_data_cleaned.csv"

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

    st.image("/Users/esra/Desktop/ulta2/recommendation-system/images/3.jpg", width=1000)
    st.write("### While my skincare recommendation engine helps match you with the right products, this section is dedicated to sharing practical skincare tips. From building a morning routine to evening care, these tips are designed to help you achieve healthy, glowing skin.")
    st.image("/Users/esra/Desktop/ulta2/recommendation-system/images/2.png", width=1000)
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
        with st.spinner("Fetching recommendations..."):
            filtered_products = data[
                (data['Skin Type Compatibility'].str.contains(skin_type, case=False, na=False)) &
                (data['Scent'].str.contains(scent, case=False, na=False) | (scent == 'All'))
            ]

            if filtered_products.empty:
                st.warning("No products found matching your criteria. Please try different preferences.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Getting initial recommendations...")
                progress_bar.progress(25)
                
                sample_product = filtered_products.iloc[0]['Product Name']
                recommended_names, recommended_brands, recommended_images, recommended_links, recommended_ease_of_use, recommended_summaries = engine.get_content_based_recommendations(
                    sample_product, skin_type, scent, top_n=40
                )
                
                progress_bar.progress(75)
                status_text.text("Preparing display...")

                BATCH_SIZE = 3
                for i in range(0, len(recommended_names), BATCH_SIZE):
                    cols = st.columns(min(BATCH_SIZE, len(recommended_names) - i))
                    
                    for j, col in enumerate(cols):
                        idx = i + j
                        if idx < len(recommended_names):
                            with col:
                                st.markdown(f"**{recommended_brands[idx]}**")
                                st.image(recommended_images[idx], 
                                    caption=recommended_names[idx], 
                                    use_container_width=True)
                                with st.expander("What customers say about this product"):
                                    st.write(f"Ease of Use: {recommended_ease_of_use[idx]}")
                                    st.write(f"Summary: {recommended_summaries[idx]}")
                                    st.write(f"[View Product]({recommended_links[idx]})")
                
                progress_bar.progress(100)
                status_text.empty()
elif selected == "Product Based Recommendation":
    st.title("Product Based Recommendation")
    st.write("Please select a product to get recommendations based on that product.")
    
    selected_product = st.selectbox("Select a product", data['Product Name'])
    
    if st.button("Get Recommendations :sparkles:"):
        with st.spinner("Fetching recommendations..."):
            recommended_names, recommended_brands, recommended_images, recommended_links, recommended_ease_of_use, recommended_summaries = engine.get_product_based_recommendations(selected_product, top_n=40)
            
            if not recommended_names:
                st.warning("No recommendations found for this product.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Preparing display...")
                progress_bar.progress(25)
                
                BATCH_SIZE = 3
                for i in range(0, len(recommended_names), BATCH_SIZE):
                    cols = st.columns(min(BATCH_SIZE, len(recommended_names) - i))
                    
                    for j, col in enumerate(cols):
                        idx = i + j
                        if idx < len(recommended_names):
                            with col:
                                st.markdown(f"**{recommended_brands[idx]}**")
                                st.image(recommended_images[idx], 
                                    caption=recommended_names[idx], 
                                    use_container_width=True)
                                with st.expander("What customers say about this product"):
                                    st.write(f"Ease of Use: {recommended_ease_of_use[idx]}")
                                    st.write(f"Summary: {recommended_summaries[idx]}")
                                    st.write(f"[View Product]({recommended_links[idx]})")
                
                progress_bar.progress(100)
                status_text.empty()

elif selected == "About":
    st.write("For More Information\n" + "https://github.com/EsraKorkmazz/skincare-product-recommendation-engine")  