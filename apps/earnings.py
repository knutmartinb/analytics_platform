import streamlit as st
import pandas as pd
import os
import datetime
import altair as alt
from apps.wind_production import load_raw_data, process_year_data
from apps.spot_prices import load_spot_prices

# Constants
DATA_YEAR = 2024

def app():
    st.title("Earnings Analysis: Høg-Jæren 2024")

    # Load production and spot price data
    df_raw = load_raw_data()
    prod_df = process_year_data(df_raw, DATA_YEAR)[["Høg-Jæren"]]
    price_df = load_spot_prices()

    # Combine datasets on timestamp
    df = prod_df.join(price_df, how="inner").dropna()
    df.columns = ["production", "price"]
    # Calculate earnings
    df["earnings"] = df["production"] * df["price"]

    # Key metrics
    total_earnings = df["earnings"].sum()
    avg_price_weighted = (df["earnings"].sum() / df["production"].sum())
    avg_monthly_earnings = df["earnings"].resample("M").sum().reset_index()

    high_day = df["earnings"].resample("D").sum().idxmax()
    high_day_value = df["earnings"].resample("D").sum().max()

    # Display KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Earnings 2024", f"{total_earnings:,.2f} €")
    k2.metric("Weighted Avg. Price", f"{avg_price_weighted:.2f} €/MWh")
    k3.metric("Highest Earning Day", f"{high_day_value:,.2f} €", delta=high_day.strftime('%Y-%m-%d'))

    st.markdown("---")
    # Earnings over time
    st.markdown("### Earnings Over Time")
    earn_ts = df.reset_index()
    line = alt.Chart(earn_ts).mark_line().encode(
        x=alt.X("timestamp:T", title="Date"),
        y=alt.Y("earnings:Q", title="Earnings (€)"),
        tooltip=["timestamp", "earnings"]
    ).properties(width="container", height=300)
    st.altair_chart(line, use_container_width=True)

    # Monthly earnings bar chart
    st.markdown("### Monthly Earnings")
    bar = alt.Chart(avg_monthly_earnings).mark_bar().encode(
        x=alt.X("timestamp:T", title="Month"),
        y=alt.Y("earnings:Q", title="Total Earnings (€)"),
        tooltip=["timestamp", "earnings"]
    ).properties(width="container", height=300)
    st.altair_chart(bar, use_container_width=True)

    # Highest/lowest earning hours
    st.markdown("### Top 10 Earning Hours")
    top10 = df["earnings"].nlargest(10).reset_index()
    top10.columns = ["Timestamp", "Earnings (€)"]
    st.dataframe(top10)

    st.markdown("### Bottom 10 Earning Hours")
    low10 = df["earnings"].nsmallest(10).reset_index()
    low10.columns = ["Timestamp", "Earnings (€)"]
    st.dataframe(low10)

    # Option: export earnings data
    st.markdown("---")
    st.download_button(
        label="Download Earnings Data",
        data=df.to_csv(index=True),
        file_name=f"hog_jaeren_earnings_{DATA_YEAR}.csv",
        mime="text/csv"
    )