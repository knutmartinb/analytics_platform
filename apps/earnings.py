import streamlit as st
import pandas as pd
import os
import altair as alt
from apps.wind_production import load_raw_data, process_year_data
from apps.spot_prices import load_spot_prices

DATA_YEAR = 2024

def app():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Select Wind Farm for Earnings")
    df_raw = load_raw_data()
    full_prod = process_year_data(df_raw, DATA_YEAR)
    farms = list(full_prod.columns)
    default = farms.index("Høg-Jæren") if "Høg-Jæren" in farms else 0
    farm = st.sidebar.selectbox("Wind farm:", farms, index=default)

    st.title(f"Earnings for {farm} in {DATA_YEAR}")

    prod = full_prod[[farm]]
    price = load_spot_prices()
    df = prod.join(price, how="inner").dropna()
    df.columns = ["production", "price"]
    df["earnings"] = df["production"] * df["price"]

    total = df["earnings"].sum()
    avg_weighted = total / df["production"].sum()
    avg_spot = df["price"].mean()
    capture = avg_weighted / avg_spot
    monthly = df["earnings"].resample("M").sum().reset_index()
    daily = df["earnings"].resample("D").sum()
    best_day = daily.idxmax(); best_val = daily.max()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Earnings", f"{total:,.2f} €")
    c2.metric("Weighted Avg Price", f"{avg_weighted:.2f} €/MWh")
    c3.metric("Average Spot Price", f"{avg_spot:.2f} €/MWh")
    c4.metric("Capture Rate", f"{capture:.2%}")
    st.markdown(f"**Highest Earning Day:** {best_day.date()} — €{best_val:,.2f}")

    st.markdown("### Earnings Over Time")
    ts = df.reset_index()
    line = alt.Chart(ts).mark_line().encode(
        x="timestamp:T", y=alt.Y("earnings:Q", title="Earnings (€)"), tooltip=["timestamp", "earnings"]
    )
    st.altair_chart(line, use_container_width=True)

    st.markdown("### Monthly Earnings")
    bar = alt.Chart(monthly).mark_bar().encode(
        x="timestamp:T", y=alt.Y("earnings:Q", title="Earnings (€)"), tooltip=["timestamp", "earnings"]
    )
    st.altair_chart(bar, use_container_width=True)

    st.markdown("### Top/Bottom Earning Hours")
    top10 = df["earnings"].nlargest(10).reset_index()
    top10.columns = ["Timestamp", "Earnings (€)"]
    low10 = df["earnings"].nsmallest(10).reset_index()
    low10.columns = ["Timestamp", "Earnings (€)"]
    st.dataframe(top10)
    st.dataframe(low10)

    st.download_button(
        label="Download Earnings CSV",
        data=df.to_csv(index=True),
        file_name=f"{farm}_earnings_{DATA_YEAR}.csv",
        mime="text/csv"
    )