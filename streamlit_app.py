import streamlit as st
from apps.wind_production import app as wind_production_app
from apps.spot_prices import app as spot_prices_app
from apps.earnings import app as earnings_app

# Define pages
PAGES = {
    "Home": None,
    "Wind Production Analysis": wind_production_app,
    "NO2 Spot Prices 2024": spot_prices_app,
    "Windfarm Earnings 2024": earnings_app,
}

st.set_page_config(page_title="Streamlit Analytics Platform", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

if selection == "Home":
    st.title("Streamlit Analytics Platform")
    st.markdown(
        """
        Welcome to your analytics platform. Use the navigation sidebar to access different analyses.

        **Available Pages**
        - **Wind Production Analysis**: Analyze wind farm production over time.
        - **NO2 Spot Prices 2024**: Explore spot price data for NO2.
        - **Windfarm Earnings 2024**: Calculate revenue for selected wind farms in 2024.
        """
    )
else:
    page = PAGES[selection]
    if page:
        page()