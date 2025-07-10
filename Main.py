# main.py

import streamlit as st
import os

# --- Page Configuration (Applies to the entire app) ---
# This should ideally be at the very top of your main.py
st.set_page_config(
    page_title="Heritage Dairy Management System",
    page_icon="🐄",
    layout="wide" # Or "centered" depending on your preference
)

# --- Global Data/Variables (if any) ---
# If you have any data or configurations that need to be accessible across all pages,
# you could load them here and potentially store them in st.session_state.
# For example, if you want to load a global DataFrame:
# try:
#     global_df = pd.read_csv("path/to/global_data.csv")
#     st.session_state['global_data'] = global_df
# except FileNotFoundError:
#     st.warning("Global data file not found.")

# --- Define the Home Page Content ---
# This content will be displayed when the user first opens the app
# or selects the 'Home' page from the sidebar.

st.title("Welcome to Heritage Dairy Management System 🐄")
st.markdown("""
    This application helps manage various aspects of dairy farming operations, including:

    * **Heritage SNF Survey**: Record and review detailed farmer and farm data.
    * **SNF Follow-up**: Track follow-up actions related to SNF (Solids-Non-Fat) measurements.
    * **Training Tracker**: Log and monitor farmer training sessions.

    Please use the navigation menu on the left to access different modules.
""")

st.info("Select a module from the sidebar to begin.")

# Optional: Add an image to the home page
# try:
#     st.image("path/to/your_dairy_image.png", caption="Happy cows!", use_column_width=True)
# except FileNotFoundError:
#     pass # Handle if image not present

# --- Sidebar Navigation (Streamlit handles automatically for 'pages' folder) ---
# Streamlit will automatically create a sidebar navigation menu
# based on the Python files it finds in the 'pages/' directory.
# You don't need to explicitly write navigation logic here for that.
# The order of pages in the sidebar will be alphabetical by default,
# or you can control it by prefixing filenames with numbers (e.g., `01_Home.py`, `02_Survey.py`).

# You can add custom elements to the sidebar in main.py if needed
st.sidebar.markdown("---")
st.sidebar.header("About the App")
st.sidebar.write("Developed for Heritage Dairy operations.")
st.sidebar.write("Version: 1.0.0")

# Note: The actual content of the other pages (like Heritage SNF Survey.py)
# will be executed when the user selects them from the sidebar.
# Ensure that each page file (e.g., 'Heritage SNF Survey.py') has its own
# st.set_page_config() if you want page-specific settings, though
# it's usually better to define a global one in main.py.
