import pandas as pd
import numpy as np

# ================= CONFIG =================
RESTAURANT_LAT = 12.9716
RESTAURANT_LNG = 77.5946


# ================= CLEAN COORDINATES =================
def preprocess_coordinates(df):
    """
    ⚡ Fast coordinate cleaning (no copy overhead)
    """
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lng'] = pd.to_numeric(df['lng'], errors='coerce')

    return df.dropna(subset=['lat', 'lng'])


# ================= HAVERSINE DISTANCE =================
def haversine_distance(df):
    """
    🚀 Ultra-fast vectorized distance (KM)
    """
    try:
        lat1 = np.radians(RESTAURANT_LAT)
        lon1 = np.radians(RESTAURANT_LNG)

        lat2 = np.radians(df['lat'])
        lon2 = np.radians(df['lng'])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            np.sin(dlat / 2) ** 2
            + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        )

        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        R = 6371  # 🌍 km

        return R * c

    except Exception as e:
        print(" Distance calc error:", e)
        return pd.Series([999999] * len(df))


# ================= ADD DISTANCE =================
def add_distance_column(df):
    """
    ⚡ Adds distance only if missing
    """
    if 'distance' not in df.columns:
        df['distance'] = haversine_distance(df)

    return df


# ================= FILTER =================
def filter_by_distance(df, max_distance):
    if max_distance is None:
        return df

    return df[df['distance'] <= max_distance]