# Skincare-Recommendation

Welcome to the **Skincare Product Recommendation Engine**, a personalized skincare assistant designed to help you find the perfect skincare products tailored to your unique skin needs and preferences.

## 📌Key Features

- **Tailored Skin Care Routine**: Get personalized product recommendations based on your specific skin concerns and goals.
- **Skin Type Analysis**: Identify your skin type and receive expert advice on the best products suited for you.
- **Product Reviews & Ratings**: Explore user reviews and ratings to make informed decisions about products.
- **Expert-backed Guidance**: Benefit from a combination of scientific knowledge, dermatological research, and real user experiences.

## Streamlit APP

[Link](https://com)

## 🛠️Technologies Used

- **Python**
- **Streamlit** for interactive web interface.
- **Pandas** for data manipulation.
- **Scikit-learn** for machine learning (cosine similarity, TF-IDF).
- **Huggingface Transformers** for text summarization using the BART model.
- **Torch** for leveraging deep learning models.
- **Streamlit Option Menu** for a neat navigation menu.

## How It Works

The **Recommendation Engine** is based on a content-based filtering approach that uses product details such as skin type compatibility, scent preference, reviews, and other product attributes. It also provides product-based recommendations where users can get recommendations similar to a selected product.

### How to Use:

1. **Home**: Learn more about the features and key aspects of the recommendation system.
2. **Recommendation**: Get personalized skincare product recommendations by selecting your skin type and scent preferences.
3. **Product Based Recommendation**: Select a specific product to see recommendations based on that product.
4. **About**: More information about the project and the GitHub repository.

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/EsraKorkmazz/Skincare-Recommendation.git
    ```

2. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the Streamlit app:
    ```bash
    streamlit run main.py
    ```

```
📂Project Structure

recommendation-system/

├── data/
   └── final_data_cleaned.csv   # Cleaned dataset used by the recommendation model
├── images/
  ├── 2.png                     # Image for the Home section
  ├── 3.jpg                     # Image for the Home section

├── recommendation_model.py          # Recommendation engine logic and methods
├── main.py                          # Streamlit app for the front end
├── requirements.txt                 # Python dependencies for the project
├── README.md                        # Project overview, setup instructions, etc.
```
