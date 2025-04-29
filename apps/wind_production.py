import streamlit as st
import pandas as pd
import os
import datetime

DATA_FILE = os.path.join("data", "vindproduksjon.xlsx")

@st.cache_data
def load_raw_data():
    """
    Read the raw Excel file (no processing).
    """
    return pd.read_excel(DATA_FILE, header=None)

@st.cache_data
def process_full_data(df_raw):
    """
    Process raw DataFrame: parse timestamps, numeric conversion, rename columns.
    Returns a DataFrame indexed by timestamp with farm names as columns.
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
    Process raw data and filter to a specific calendar year.
    """
    df = process_full_data(df_raw)
    mask = df.index.year == year
    df_year = df.loc[mask].copy()
    df_year = df_year.infer_objects()
    return df_year

def app():
    st.title("Wind Production Analysis")

    df_raw = load_raw_data()
    full_df = process_full_data(df_raw)
    farm_names = list(full_df.columns)

    # Defaults to Høg-Jæren
    st.sidebar.markdown("---")
    st.sidebar.subheader("Wind Farm Selection")
    default_selected = ["Høg-Jæren"] if "Høg-Jæren" in farm_names else [farm_names[0]]
    selected = st.sidebar.multiselect("Select wind farms:", farm_names, default_selected)

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

    filtered = data_df.loc[start:end, selected]

    st.markdown("### Production Over Time")
    st.line_chart(filtered, y=selected)

    st.markdown("### Data Table")
    with st.expander("Show raw data"):
        st.dataframe(filtered)
