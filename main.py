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

def categorize_transactions(df):
    df["Category"] = "Uncategorized"

    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue

        lowered_keywords = [keyword.lower().strip() for keyword in keywords]

        for idx, row in df.iterrows():
            details = row["Description"].lower()
            if details in lowered_keywords:
                df.at[idx, "Category"] = category
    return df

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True
    return False

# Function to load and clean transactions from an uploaded CSV
def load_transactions(file):
    try:
        # Read the uploaded CSV into a pandas DataFrame
        df = pd.read_csv(file)
        # Strip extra spaces from column names
        df.columns = [col.strip() for col in df.columns]
        return categorize_transactions(df)

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
            st.session_state.df = df.copy()
            new_category = st.text_input("New Category Name")
            add_button = st.button("Add Category")

            if add_button and new_category:
                if new_category not in st.session_state.categories:
                    st.session_state.categories[new_category] = []
                    save_categories()
                    st.rerun()
            st.subheader("Your Expenses")
            edited_df = st.data_editor(
                st.session_state.df, column_config={
                    "Date":st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                    "Amount":st.column_config.NumberColumn("Amount", format="%.2f CAD"),
                    "Category":st.column_config.SelectboxColumn(
                        "Category",
                        options=list(st.session_state.categories.keys())
                    )
                },
                hide_index=True,
                use_container_width=True,
                key="category_editor"
            )
            save_button = st.button("Apply Changes", type="primary")
            if save_button:
                for idx, row in edited_df.iterrows():
                    new_category = row["Category"]
                    if row["Category"] == st.session_state.df.at[idx,"Category"]:
                        continue
                    details = row["Description"]
                    st.session_state.df.at[idx,"Category"] = new_category
                    add_keyword_to_category(new_category, details)

            st.subheader("Expense Summary")
            category_totals = st.session_state.df.groupby("Category")["Amount"].sum().reset_index()
            category_totals = category_totals.sort_values("Amount", ascending=False)

            st.dataframe(
                category_totals,
                use_container_width=True,
                hide_index=True
            )

            fig = px.pie(
                category_totals,
                values="Amount",
                names="Category",
                title="Expenses by Category"
            )
            st.plotly_chart(fig, use_container_width=True)

main()