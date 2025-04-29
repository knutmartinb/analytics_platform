import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    # Load the Excel file from the data folder
    file_path = os.path.join("data", "vindproduksjon.xlsx")
    df = pd.read_excel(file_path, header=None)
    return df


def app():
    st.title("Wind Production Analysis")
    df = load_data()

    # Parse headers: row 1 (index 0) has names, row 2 (index 1) has IDs
    windfarm_names = df.iloc[0, 1:].tolist()
    windfarm_ids = df.iloc[1, 1:].tolist()

    # Data from row 4 onwards (index 3+) and columns A (timestamp) + farms
    data = df.iloc[3:, :]
    data.columns = ["timestamp"] + windfarm_ids
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data = data.set_index("timestamp")

    # Sidebar filters specific to this page
    st.sidebar.markdown("---")
    st.sidebar.subheader("Wind Farm Selection")
    selected_plants = st.sidebar.multiselect(
        "Select wind farms to display:",
        options=windfarm_ids,
        default=windfarm_ids
    )

    st.sidebar.subheader("Date Range")
    min_date = data.index.min().date()
    max_date = data.index.max().date()
    start_date, end_date = st.sidebar.date_input(
        "Choose date range:",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    # Filter data
    filtered = data.loc[start_date:end_date, selected_plants]

    # Main visualizations
    st.markdown("### Production Over Time")
    st.line_chart(filtered)

    st.markdown("### Data Table")
    with st.expander("Show raw data"):
        st.dataframe(filtered)
