import numpy as np
import pandas as pd


# ================= DIRECTION =================
def apply_direction(df, center_lat, center_lng):

    if df.empty or "lat" not in df.columns or "lng" not in df.columns:
        df["direction"] = "Unknown"
        return df

    lat_diff = df["lat"] - center_lat
    lng_diff = df["lng"] - center_lng

    df["direction"] = np.where(
        abs(lat_diff) > abs(lng_diff),
        np.where(lat_diff > 0, "North", "South"),
        np.where(lng_diff > 0, "East", "West")
    )

    return df


# ================= FILTERS =================
def apply_filters(df, search_id, direction, segment, distance, distance_ready):

    if df.empty:
        return df

    filtered_df = df.copy()

    # 🔍 Search filter
    if search_id and "customer_id" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["customer_id"]
            .astype(str)
            .str.contains(search_id, case=False, na=False)
        ]

    # 🧭 Direction filter
    if direction != "All" and "direction" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["direction"] == direction]

    # 👥 Segment filter
    if segment != "All" and "segment" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["segment"] == segment]

    # 📏 Distance filter
    if distance_ready and distance is not None and "distance" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["distance"] <= distance]

    return filtered_df


# ================= GEO FILTER =================
def filter_nearby_customers(df, center_lat, center_lng, radius):

    if df.empty or "lat" not in df.columns or "lng" not in df.columns:
        return df

    lat_diff = (df["lat"] - center_lat) * 111000
    lng_diff = (df["lng"] - center_lng) * 111000

    distance = np.sqrt(lat_diff**2 + lng_diff**2)

    df["calculated_distance"] = distance

    return df[df["calculated_distance"] <= radius]


# ================= SEGMENTATION =================
def apply_segmentation(df):

    if df.empty:
        df["segment"] = "Unknown"
        return df

    # ✅ ensure visits column exists
    if "visits" not in df.columns:
        df["visits"] = 0

    # ✅ convert safely
    df["visits"] = pd.to_numeric(df["visits"], errors="coerce").fillna(0)

    # ✅ CORRECT SEGMENTATION LOGIC
    df["segment"] = np.select(
        [
            df["visits"] <= 1,
            (df["visits"] > 1) & (df["visits"] <= 5),
            (df["visits"] > 5) & (df["visits"] <= 10),
            df["visits"] > 10
        ],
        [
            "New",
            "Regular",
            "Frequent",
            "Loyal"
        ],
        default="New"
    )

    return df