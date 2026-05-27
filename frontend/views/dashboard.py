import streamlit as st
import pandas as pd
import numpy as np
from services.processing import apply_segmentation
from services.processing import apply_direction, apply_filters
from utils.helpers import convert_to_meters
from config import CENTER_LAT, CENTER_LNG
from geopy.geocoders import Nominatim
from services.api import fetch_restaurants

from streamlit_folium import st_folium
import folium


# =================  CACHED PROCESSING =================
@st.cache_data(show_spinner=False)
def cached_process(df, rest_lat, rest_lng):

    if df.empty or "lat" not in df.columns or "lng" not in df.columns:
        return pd.DataFrame()

    df = df.copy()

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    df = df.dropna(subset=["lat", "lng"])

    # ✅ FIX VISITS
# ✅ FORCE VISITS COLUMN (STRICT FIX)
    if "visits" in df.columns:
        df["visits"] = df["visits"]

    elif "visit_count" in df.columns:
        df["visits"] = df["visit_count"]

    elif "visits " in df.columns:   # 🔥 handle space issue
        df["visits"] = df["visits "]

    else:
        st.error(f"❌ Visits column not found. Available: {list(df.columns)}")
        df["visits"] = 0

    # 🔥 CLEAN COLUMN NAMES (VERY IMPORTANT)
    df.columns = df.columns.str.strip()

    # 🔥 FORCE NUMERIC
    df["visits"] = pd.to_numeric(df["visits"], errors="coerce")

    # 🔥 DEBUG
    DEBUG = False

    if DEBUG:
        st.write("VISITS AFTER CLEAN:", df["visits"].head())

    # 🔥 HANDLE NaN
    df["visits"] = df["visits"].fillna(0)
    # ✅ APPLY SEGMENTATION
    df = apply_segmentation(df)

    df = compute_distance(df, rest_lat, rest_lng)
    df = apply_direction(df, rest_lat, rest_lng)

    return df

@st.cache_data(show_spinner=False)
def cached_filter(df, search_id, direction_filter, segment_filter, distance, distance_ready):
    return apply_filters(
        df,
        search_id,
        direction_filter,
        segment_filter,
        distance,
        distance_ready
    )


# ================= CONFIG =================
MAX_POINTS = 500


@st.cache_resource
def get_geo():
    return Nominatim(user_agent="geoapp")


@st.cache_data
def geocode_place(place):
    geo = get_geo()
    return geo.geocode(place, timeout=5)


@st.cache_data
def compute_distance(df, rest_lat, rest_lng):
    R = 6371000
    lat1 = np.radians(rest_lat)
    lon1 = np.radians(rest_lng)
    lat2 = np.radians(df["lat"].values)
    lon2 = np.radians(df["lng"].values)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    df["distance"] = R * c
    return df


@st.cache_data(show_spinner=False)
def cached_map(rest_lat, rest_lng, filtered_df, distance, distance_ready):
    m = folium.Map(location=[rest_lat, rest_lng], zoom_start=14)

    folium.Marker([rest_lat, rest_lng], icon=folium.Icon(color="red")).add_to(m)

    if distance_ready:
        folium.Circle(
            location=[rest_lat, rest_lng],
            radius=distance,
            color="blue",
            fill=True,
            fill_opacity=0.1
        ).add_to(m)

    for row in filtered_df.itertuples():
        folium.CircleMarker(
            location=[row.lat, row.lng],
            radius=3
        ).add_to(m)

    return m


# ================= MAIN =================
def show():

    st.title("Smart Geo Dashboard")

    # ================= SESSION =================
    if "center_lat" not in st.session_state:
        st.session_state.center_lat = CENTER_LAT
    if "center_lng" not in st.session_state:
        st.session_state.center_lng = CENTER_LNG

    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame()
# ================= 🔥 AUTO FETCH CUSTOMER DATA =================
    import requests


    def fetch_customers():
        try:
            res = requests.get("http://127.0.0.1:8000/api/customers")
            if res.status_code == 200:
                data = res.json()
                return pd.DataFrame(data)
            return pd.DataFrame()
        except:
            return pd.DataFrame()


    # Auto load from DB if not already loaded

    df_db = fetch_customers()

    # always update session state
    st.session_state.data = df_db

    if df_db.empty:
        st.warning(" No customer data found in database")
    else:
        st.success(f"Loaded {len(df_db)} customers from database")


    # ================= LOCATION =================

    # ✅ INITIALIZATION
    if "mode" not in st.session_state:
        st.session_state.mode = "both"

    if "search" not in st.session_state:
        st.session_state.search = ""

    if "dropdown" not in st.session_state:
        st.session_state.dropdown = "-- Select --"

    # ✅ NEW: persistent messages
    if "search_error" not in st.session_state:
        st.session_state.search_error = ""

    if "search_success" not in st.session_state:
        st.session_state.search_success = ""


    st.subheader(" Select Restaurant Location")

    restaurants = fetch_restaurants()
    names = [r["name"] for r in restaurants] if restaurants else []

    col1, col2 = st.columns(2)


    # ================= DROPDOWN =================
    with col1:
        if st.session_state.mode in ["both", "dropdown"]:

            selected = st.selectbox(
                "🏨 Select Restaurant",
                ["-- Select --"] + names,
                key="dropdown"
            )

            if selected != "-- Select --":
                selected_data = next(
                    (r for r in restaurants if r["name"] == selected),
                    None
                )

                if selected_data:
                    st.session_state.center_lat = selected_data["lat"]
                    st.session_state.center_lng = selected_data["lng"]
                    st.session_state.mode = "dropdown"

                    # clear messages
                    st.session_state.search_error = ""
                    st.session_state.search_success = ""

                    st.success(f"Selected: {selected}")


    # ================= SEARCH =================
    def handle_search():
        place = st.session_state.get("search", "")

        # clear old messages
        st.session_state.search_error = ""
        st.session_state.search_success = ""

        if not place.strip():
            st.session_state.search_error = " Please enter a location"
            return

        loc = geocode_place(place)

        if loc:
            st.session_state.center_lat = loc.latitude
            st.session_state.center_lng = loc.longitude
            st.session_state.mode = "search"

            st.session_state.search_success = f" {loc.address}"
        else:
            st.session_state.search_error = " Location not found"


    with col2:
        if st.session_state.mode in ["both", "search"]:

            st.text_input(
                "Search location",
                key="search",
                on_change=handle_search
            )

            # ✅ persistent messages (FIXED ISSUE)
            if st.session_state.search_error:
                st.warning(st.session_state.search_error)

            if st.session_state.search_success:
                st.success(st.session_state.search_success)


    # ================= RESET (CENTERED BELOW) =================
    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_mid, col_right = st.columns([1, 2, 1])

    with col_mid:
        if st.button(" Reset Location", use_container_width=True):
            st.session_state.mode = "both"

            st.session_state.pop("dropdown", None)
            st.session_state.pop("search", None)

            # clear messages
            st.session_state.search_error = ""
            st.session_state.search_success = ""

            st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        lat = st.number_input("Latitude", value=float(st.session_state.center_lat), format="%.6f")

    with col2:
        lng = st.number_input("Longitude", value=float(st.session_state.center_lng), format="%.6f")

    if st.button(" Update from Coordinates"):
        st.session_state.center_lat = lat
        st.session_state.center_lng = lng

    rest_lat = st.session_state.center_lat
    rest_lng = st.session_state.center_lng

    # ================= EMPTY STATE =================
    # no_data = st.session_state.data.empty

    # if no_data:
    #     m = folium.Map(location=[rest_lat, rest_lng], zoom_start=14)
    #     folium.Marker([rest_lat, rest_lng], tooltip="Restaurant").add_to(m)

    #     st_folium(m, width=900, height=400, key="empty_map")

    # ================= DATA =================
    if not st.session_state.data.empty:
        df = cached_process(
            st.session_state.data,
            rest_lat,
            rest_lng
        )
    else:
        df = pd.DataFrame()
    # ================= FILTERS =================
    st.sidebar.subheader("Filters")

    search_id = st.sidebar.text_input("Customer ID")

    segment_filter = st.sidebar.selectbox(
        "Segment", ["All", "New", "Regular", "Frequent"]
    )

    direction_filter = st.sidebar.selectbox(
        "Direction", ["All", "North", "South", "East", "West"]
    )

    distance_option = st.sidebar.selectbox(
        "Distance",
        ["100 m", "200 m", "500 m", "1 km", "2 km", "5 km", "Custom"]
    )

    if distance_option == "Custom":
        custom_input = st.sidebar.text_input("Enter distance")
        distance = convert_to_meters(custom_input) if custom_input else None
        distance_ready = distance is not None
    else:
        distance = convert_to_meters(distance_option)
        distance_ready = True



    # ================= PROCESS =================
    # df = compute_distance(df, rest_lat, rest_lng)
    # df = apply_direction(df, rest_lat, rest_lng)
    if not df.empty:
        filtered_df = cached_filter(
            df,
            search_id,
            direction_filter,
            segment_filter,
            distance,
            distance_ready
        )
    else:
        filtered_df = pd.DataFrame()

    if len(filtered_df) > MAX_POINTS:
        filtered_df = filtered_df.sample(MAX_POINTS)

    st.session_state.filtered_data = filtered_df
    st.session_state.data_version = st.session_state.get("data_version", 0) + 1
    # ================= 🔥 LIVE FILTER SUMMARY =================
    st.sidebar.markdown("### Filter Summary")

    st.sidebar.write(f"Customers: {len(filtered_df)}")

    if distance_ready and distance is not None:
        st.sidebar.write(f"Distance: {int(distance)} m")

   # ================= MAP =================
    no_data = st.session_state.data.empty
    st.subheader("🗺 Interactive Map")

    if no_data:
        # ✅ show ONLY empty map
        m = folium.Map(location=[rest_lat, rest_lng], zoom_start=14)
        folium.Marker([rest_lat, rest_lng]).add_to(m)

        map_data = st_folium(m, width=900, height=400, key="empty_map")

    else:
        # ✅ show ONLY main map
        m = folium.Map(location=[rest_lat, rest_lng], zoom_start=14)

        folium.Marker([rest_lat, rest_lng], icon=folium.Icon(color="red")).add_to(m)

        if distance_ready:
            folium.Circle(
                location=[rest_lat, rest_lng],
                radius=distance,
                color="blue",
                fill=True,
                fill_opacity=0.1
            ).add_to(m)

        if not filtered_df.empty:
            for row in filtered_df.itertuples():
                folium.CircleMarker(
                    location=[row.lat, row.lng],
                    radius=3
                ).add_to(m)

        map_data = st_folium(m, width=900, height=500, key="main_map")


    # ================= CLICK UPDATE =================
    if map_data and map_data.get("last_clicked"):
        new_lat = map_data["last_clicked"]["lat"]
        new_lng = map_data["last_clicked"]["lng"]

        st.session_state.center_lat = new_lat
        st.session_state.center_lng = new_lng

        st.success(f"Updated Location: {new_lat:.5f}, {new_lng:.5f}")
    # ================= METRICS =================

    st.subheader(" Metrics")

    if not filtered_df.empty:
        total_customers = len(filtered_df)

        nearby_count = (
            (filtered_df["distance"] <= distance).sum()
            if "distance" in filtered_df.columns and distance_ready
            else 0
        )

        frequent_count = (
            (filtered_df["segment"] == "Frequent").sum()
            if "segment" in filtered_df.columns
            else 0
        )
    else:
        total_customers = 0
        nearby_count = 0
        frequent_count = 0


    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", total_customers)
    col2.metric("Nearby Customers", nearby_count)
    col3.metric("Frequent Customers", frequent_count)
  
    # ================= TABLE =================
    st.subheader("Customers")

    table_df = filtered_df.copy().reset_index(drop=True)

    table_df.insert(0, "S.No", table_df.index + 1)
    table_df["Customer ID"] = table_df.get("customer_id", "")
    if "distance" in table_df.columns:
        table_df["Distance (m)"] = table_df["distance"].fillna(0).astype(int)
    else:
        table_df["Distance (m)"] = 0
    table_df["Latitude"] = table_df["lat"] if "lat" in table_df.columns else 0
    table_df["Longitude"] = table_df["lng"] if "lng" in table_df.columns else 0

    table_df["Direction"] = table_df["direction"] if "direction" in table_df.columns else "N/A"
    table_df["Segment"] = table_df["segment"] if "segment" in table_df.columns else "N/A"
    if "utc_timestamp" in table_df.columns:
        table_df["Last Seen"] = pd.to_datetime(table_df["utc_timestamp"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M")
    else:
        table_df["Last Seen"] = "N/A"

    table_df["Actions"] = "View"

    final_cols = [
        "S.No", "Customer ID", "Distance (m)",
        "Latitude", "Longitude",
        "Direction", "Segment",
        "Last Seen", "Actions"
    ]

    st.dataframe(table_df[final_cols], use_container_width=True)