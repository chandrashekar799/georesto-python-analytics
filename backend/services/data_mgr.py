from backend.db.supabase_client import supabase
import pandas as pd
import numpy as np
import time
from threading import Lock

from backend.services.geo_calc import preprocess_coordinates

# ================= CONFIG =================
CACHE_TTL = 120  # seconds

# Restaurant location (update if needed)
RESTAURANT_LAT = 12.9716
RESTAURANT_LNG = 77.5946

# ================= THREAD SAFE CACHE =================
_cache = {
    "data": None,
    "timestamp": 0
}
cache_lock = Lock()


# ================= FAST SEGMENT LOGIC =================
def assign_segment_vectorized(visits_series):
    visits = pd.to_numeric(visits_series, errors="coerce").fillna(0)

    conditions = [
        visits <= 1,
        visits <= 3,
        visits <= 7,
        visits > 7
    ]

    choices = ["New", "Regular", "Frequent", "Loyal"]

    return np.select(conditions, choices, default="New")


# ================= FAST DISTANCE (HAVERSINE) =================
def haversine(lat, lon):
    R = 6371  # km

    lat1 = np.radians(RESTAURANT_LAT)
    lon1 = np.radians(RESTAURANT_LNG)
    lat2 = np.radians(lat)
    lon2 = np.radians(lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c


# ================= LOAD DATA =================
def load_all_customers():
    """
     High-performance cached loader
    """

    current_time = time.time()

    with cache_lock:
        # ✅ Use cache
        if _cache["data"] is not None and (current_time - _cache["timestamp"] < CACHE_TTL):
            print("⚡ Using cached data")
            return _cache["data"]

        try:
            print(" Fetching fresh data from Supabase...")

            response = supabase.table("customers").select("*").execute()
            data = response.data

            if not data:
                print(" No data from Supabase")
                return pd.DataFrame()

            df = pd.DataFrame(data)

            # ================= CLEAN =================
            df = preprocess_coordinates(df)

            # ================= SEGMENT (FAST) =================
            if "visits" in df.columns:
                df["segment"] = assign_segment_vectorized(df["visits"])

            # ================= DISTANCE (FAST) =================
            if "lat" in df.columns and "lng" in df.columns:
                df["distance"] = haversine(df["lat"], df["lng"])

            # ================= CACHE STORE =================
            _cache["data"] = df
            _cache["timestamp"] = current_time

            print(f"Loaded {len(df)} customers (cached)")

            return df

        except Exception as e:
            print("Supabase Fetch Error:", e)
            return pd.DataFrame()


# ================= FILTER FUNCTION =================
def get_customers(
    min_distance=0,
    max_distance=None,
    segment="All"
):
    """
    Ultra-fast filtering (in-memory)
    """

    df = load_all_customers()

    if df.empty:
        return df

    # ================= SEGMENT FILTER =================
    if segment != "All" and "segment" in df.columns:
        df = df[df["segment"] == segment]

    # ================= DISTANCE FILTER =================
    if max_distance is not None and "distance" in df.columns:
        df = df[
            (df["distance"] >= min_distance) &
            (df["distance"] <= max_distance)
        ]

    return df


# ================= CLEAR CACHE =================
def clear_cache():
    """
    🔥 Call after upload
    """
    with cache_lock:
        _cache["data"] = None
        _cache["timestamp"] = 0
    print("Cache cleared")