import streamlit as st
from pages.wind_production import app as wind_production_app

# Define available pages
PAGES = {
    "Home": None,
    "Wind Production Analysis": wind_production_app,
}

st.set_page_config(page_title="Streamlit Analytics Platform", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

if selection == "Home":
    # Front page content
    st.title("Streamlit Analytics Platform")
    st.markdown(
        """
        Welcome to your analytics platform. Use the navigation sidebar to access different analyses.

        **Available Pages**
        - **Wind Production Analysis**: Analyze wind farm production over time, visualize trends, and explore data.
        """
    )
else:
    # Render the selected page
    page = PAGES[selection]
    if page:
        page()