import requests
import pandas as pd
from config import BACKEND_URL


# ✅ FETCH CUSTOMERS (WITH FILTERS)
def get_customers_data(min_dist=0, max_dist=10000, segment="All", max_distance=None):
    try:
        res = requests.get(
            f"{BACKEND_URL}/api/customers",
            params={
                "min_dist": min_dist,
                "max_dist": max_dist,
                "segment": segment,
                "max_distance": max_distance
            }
        )

        if res.status_code == 200:
            data = res.json()

            # ✅ FIX: handle both list & dict
            if isinstance(data, list):
                return pd.DataFrame(data)

            return pd.DataFrame(data.get("data", []))

        else:
            print("❌ API Error:", res.status_code, res.text)

    except Exception as e:
        print("❌ Request failed:", e)

    return pd.DataFrame()


# ✅ DASHBOARD STATS
def fetch_stats():
    try:
        res = requests.get(f"{BACKEND_URL}/api/dashboard")

        if res.status_code == 200:
            return res.json()

        else:
            print("❌ Stats API Error:", res.status_code)

    except Exception as e:
        print("❌ Stats request failed:", e)

    return {
        "total_customers": 0,
        "nearby": 0,
        "frequent": 0
    }


# ✅ FILE UPLOAD (CUSTOMERS)
def upload_csv(file):
    try:
        files = {"file": file}
        res = requests.post(f"{BACKEND_URL}/api/upload", files=files)

        if res.status_code == 200:
            return res.json()

        else:
            return {
                "status": "error",
                "message": res.text
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ================= 🏨 RESTAURANTS =================

# ✅ FETCH RESTAURANTS (FIXED)
def fetch_restaurants():
    try:
        res = requests.get(f"{BACKEND_URL}/api/restaurants")

        if res.status_code == 200:
            data = res.json()

            # ✅ FIX: handle list response
            if isinstance(data, list):
                return data

            return data.get("data", [])

        else:
            print("❌ Restaurants API Error:", res.status_code)

    except Exception as e:
        print("❌ Restaurants request failed:", e)

    return []


# ✅ UPLOAD RESTAURANTS
def upload_restaurants(file):
    try:
        files = {"file": file}
        res = requests.post(f"{BACKEND_URL}/api/upload-restaurants", files=files)

        if res.status_code == 200:
            return res.json()

        else:
            return {
                "status": "error",
                "message": res.text
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }