import streamlit as st
import pandas as pd
import plotly.express as px


def show():

    st.title("📊 Analytics Dashboard")

    # ================= LOAD DATA =================
    if "data" not in st.session_state or st.session_state.data.empty:
        st.warning("No data available. Please upload data first.")
        return

    df = st.session_state.data.copy()

    # ================= CLEAN =================
    if "distance" in df.columns:
        df["distance"] = pd.to_numeric(df["distance"], errors="coerce")

    # ================= FILTERS =================
    st.sidebar.subheader("🔍 Filters")

    segment = st.sidebar.selectbox(
        "Segment",
        ["All", "New", "Regular", "Frequent"]
    )

    max_distance_input = st.sidebar.text_input(
        "Max Distance (meters)",
        placeholder="e.g., 2000"
    )

    # ================= APPLY FILTER =================
    filtered_df = df.copy()

    # Segment filter
    if segment != "All" and "segment" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["segment"] == segment]

    # Distance filter
    if max_distance_input.strip():
        try:
            max_distance = float(max_distance_input)

            filtered_df = filtered_df[
                (filtered_df["distance"].notna()) &
                (filtered_df["distance"] <= max_distance)
            ]

        except:
            st.sidebar.error("Enter valid distance")

    # ================= KPI =================
    st.subheader("📈 Key Metrics")

    total = len(filtered_df)

    col1, col2 = st.columns(2)

    col1.metric("Total Customers", total)

    avg_dist = (
        int(filtered_df["distance"].mean())
        if "distance" in filtered_df.columns and not filtered_df.empty
        else 0
    )

    col2.metric("Avg Distance (m)", avg_dist)

    st.caption(f"Showing {total} customers after filters")

    # ================= CHART 1 =================
    st.subheader("Customer Segments")

    if not filtered_df.empty and "segment" in filtered_df.columns:

        seg_df = (
            filtered_df["segment"]
            .value_counts()
            .reset_index()
        )
        seg_df.columns = ["segment", "count"]

        fig_bar = px.bar(
            seg_df,
            x="segment",
            y="count",
            text="count"
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.info("No segment data available")

    # ================= CHART 2 =================
    st.subheader("Distance Distribution")

    if not filtered_df.empty and "distance" in filtered_df.columns:

        fig_hist = px.histogram(
            filtered_df,
            x="distance",
            nbins=20
        )

        st.plotly_chart(fig_hist, use_container_width=True)

    else:
        st.info("No distance data available")

    # ================= TABLE =================
    st.subheader("Filtered Data")

    if not filtered_df.empty:
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("No data after applying filters")