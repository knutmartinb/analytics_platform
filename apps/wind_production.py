import streamlit as st
import pandas as pd
import os
import datetime
import random

DATA_FILE = os.path.join("data", "vindproduksjon.xlsx")

@st.cache_data
def load_raw_data():
    """Load raw Excel data without processing."""
    return pd.read_excel(DATA_FILE, header=None)

@st.cache_data
def process_full_data(df_raw):
    """
    Process raw DataFrame:
    - Parse timestamps
    - Convert to numeric
    - Rename columns from IDs to farm names
    """
    farm_names = [str(x) for x in df_raw.iloc[0, 1:].tolist()]
    farm_ids = [str(x) for x in df_raw.iloc[1, 1:].tolist()]
    id2name = dict(zip(farm_ids, farm_names))

    df = df_raw.iloc[3:, :].copy()
    df.columns = ["timestamp"] + farm_ids
    df.loc[:, "timestamp"] = pd.to_datetime(df.loc[:, "timestamp"], errors="coerce")
    df = df.set_index("timestamp")
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.rename(columns=id2name)
    df = df.infer_objects()
    return df

@st.cache_data
def process_year_data(df_raw, year):
    """
    Filter processed DataFrame to a specific year.
    """
    df = process_full_data(df_raw)
    df_year = df[df.index.year == year].copy()
    return df_year

@st.cache_data
def get_farm_locations(farms):
    """
    Generate random coordinates within Norway for each farm.
    """
    random.seed(42)
    locs = {}
    for farm in farms:
        lat = random.uniform(57.5, 71.5)
        lon = random.uniform(4.5, 31.0)
        locs[farm] = (lat, lon)
    return locs


def app():
    st.title("Wind Production Analysis")

    # Load and process data
    df_raw = load_raw_data()
    full_df = process_full_data(df_raw)
    farms = list(full_df.columns)

    # Sidebar: farm selection
    st.sidebar.markdown("---")
    st.sidebar.subheader("Wind Farm Selection")
    default_farm = "Høg-Jæren" if "Høg-Jæren" in farms else farms[0]
    selected_farms = st.sidebar.multiselect(
        "Select wind farms:", farms, default=[default_farm]
    )

    # Sidebar: date range
    st.sidebar.subheader("Date Range")
    min_date = full_df.index.min().date()
    max_date = full_df.index.max().date()
    default_start = datetime.date(2024, 1, 1)
    default_end = datetime.date(2024, 12, 31)
    default_start = max(min_date, default_start)
    default_end = min(max_date, default_end)
    show_all = st.sidebar.checkbox("Show full date range", value=False)

    data_df = full_df if show_all else process_year_data(df_raw, 2024)

    start, end = st.sidebar.date_input(
        "Choose date range:",
        [default_start if not show_all else min_date,
         default_end if not show_all else max_date],
        min_value=min_date,
        max_value=max_date
    )

    filtered = data_df.loc[start:end, selected_farms]

    # Main visuals
    st.markdown("### Production Over Time")
    st.line_chart(filtered, y=selected_farms)

    st.markdown("### Data Table")
    with st.expander("Show raw data"):
        st.dataframe(filtered)

    # Map of Wind Farms
    st.markdown("### Map of Wind Farms")
    locs = get_farm_locations(farms)
    map_df = pd.DataFrame(
        [{"farm": f, "lat": locs[f][0], "lon": locs[f][1]} for f in farms]
    )
    st.map(map_df.rename(columns={"lat": "latitude", "lon": "longitude"}))

    st.markdown("**Farm Locations**")
    st.dataframe(map_df.set_index("farm"))