import streamlit as st
import pandas as pd
import os
import altair as alt

DATA_FILE = os.path.join("data", "NO2_price_2024.xlsx")

@st.cache_data
def load_spot_prices():
    """
    Load NO2 spot price data for 2024 from Excel.
    Assumes first column is timestamp and second is price.
    """
    df = pd.read_excel(DATA_FILE, parse_dates=[0])
    df.columns = ["timestamp", "price"]
    df = df.set_index("timestamp")
    return df


def app():
    st.title("NO2 Spot Prices 2024 (€/MWh)")
    df = load_spot_prices()

    # Time series with Altair
    st.markdown("### Price Over Time")
    time_df = df.reset_index()
    line = alt.Chart(time_df).mark_line().encode(
        x=alt.X("timestamp:T", title="Date"),
        y=alt.Y("price:Q", title="Price (€/MWh)")
    ).properties(width="container", height=300)
    st.altair_chart(line, use_container_width=True)

    # Key metrics
    avg_year = df["price"].mean()
    col1, col2 = st.columns(2)
    col1.metric("Average Price 2024", f"{avg_year:.2f} €/MWh")
    col2.empty()

    # Monthly averages
    monthly = df["price"].resample("M").mean().reset_index()
    st.markdown("### Monthly Average Prices")
    bar = alt.Chart(monthly).mark_bar().encode(
        x=alt.X("timestamp:T", title="Month"),
        y=alt.Y("price:Q", title="Average Price (€/MWh)")
    ).properties(width="container", height=300)
    st.altair_chart(bar, use_container_width=True)

    # Highest and lowest
    st.markdown("### Top 10 Highest Price Hours")
    top10 = df["price"].nlargest(10).reset_index()
    top10.columns = ["Timestamp", "Price (€/MWh)"]
    st.dataframe(top10)

    st.markdown("### Top 10 Lowest Price Hours")
    low10 = df["price"].nsmallest(10).reset_index()
    low10.columns = ["Timestamp", "Price (€/MWh)"]
    st.dataframe(low10)