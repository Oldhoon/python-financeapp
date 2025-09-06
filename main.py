import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Finance App", page_icon="💰", layout="wide")

CATEGORY_FILE = "categories.json"

# Initialize session state to hold categories if not already created
# st.session_state is like a persistent dictionary across user interactions
if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": []
    }

if os.path.exists(CATEGORY_FILE):
    with open(CATEGORY_FILE, "r") as f:
        st.session_state.categories = json.load(f)

def save_categories():
    with open(CATEGORY_FILE, "w") as f:
        json.dump(st.session_state.categories, f)

# Function to load and clean transactions from an uploaded CSV
def load_transactions(file):
    try:
        # Read the uploaded CSV into a pandas DataFrame
        df = pd.read_csv(file)
        # Strip extra spaces from column names
        df.columns = [col.strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None


def main():
    # Display the dashboard title
    st.title("Dashboard")
    # File uploader widget: allows user to upload a CSV file
    uploaded_file = st.file_uploader("Upload Bank Statement CSV file", type=["csv"])

    # load file if file exists
    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

        # If data was successfully loaded, display the DataFrame
        if df is not None:
            new_category = st.text_input("New Category Name")
            add_button = st.button("Add Category")

            if add_button and new_category:
                if new_category not in st.session_state.categories:
                    st.session_state.categories[new_category] = []
                    save_categories()
                    st.rerun()
            st.write(df)



main()