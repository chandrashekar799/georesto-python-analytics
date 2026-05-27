import streamlit as st
import pandas as pd


def show():

    st.title("📢 Campaign Manager")

    # ================= LOAD DATA =================
    if "data" not in st.session_state or st.session_state.data.empty:
        st.warning("No data available. Please upload data first.")
        return

    df = st.session_state.data.copy()

    # ✅ Fix distance column
    if "distance" in df.columns:
        df["distance"] = pd.to_numeric(df["distance"], errors="coerce")

    # ================= CAMPAIGN FORM =================
    st.subheader("✉️ Create Campaign")

    campaign_name = st.text_input("Campaign Name")
    message = st.text_area("Message")

    # ================= FILTERS =================
    st.subheader("🎯 Target Filters")

    col1, col2 = st.columns(2)

    with col1:
        segment = st.selectbox(
            "Customer Segment",
            ["All", "New", "Regular", "Frequent"]
        )

    with col2:
        max_distance_input = st.text_input(
            "Max Distance (meters)",
            placeholder="Enter distance (e.g., 2000)"
        )

    # ================= VALIDATE DISTANCE =================
    if max_distance_input.strip() == "":
        st.info("Enter distance to filter customers")
        return

    try:
        max_distance = float(max_distance_input)

        if max_distance < 0 or max_distance > 10_000_000:
            st.error("Distance must be between 0 and 10,000,000")
            return

    except:
        st.error("Enter valid numeric distance")
        return

    # ================= APPLY FILTER =================
    filtered_df = df.copy()

    # Segment filter
    if segment != "All" and "segment" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["segment"] == segment]

    # Distance filter
    if "distance" in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df["distance"].notna()) &
            (filtered_df["distance"] <= max_distance)
        ]

    # ================= TARGET =================
    st.subheader("👥 Target Audience")

    total = len(filtered_df)
    st.metric("Customers to Target", total)

    st.caption(f"Showing customers within {max_distance} meters")

    if total > 0:

        cols = [
            c for c in ["customer_id", "distance", "segment"]
            if c in filtered_df.columns
        ]

        display_df = filtered_df[cols].sort_values("distance").reset_index(drop=True)

        # ✅ Serial number column
        display_df.insert(0, "S.No", range(1, len(display_df) + 1))

        st.dataframe(display_df, use_container_width=True)

    else:
        st.warning("No customers match filters")

    # ================= SEND =================
    if st.button("🚀 Send Campaign", use_container_width=True):

        if not campaign_name.strip():
            st.warning("Enter campaign name")
            return

        if not message.strip():
            st.warning("Enter message")
            return

        if total == 0:
            st.warning("No customers to send")
            return

        st.success(f"Campaign '{campaign_name}' sent to {total} customers 🎉")