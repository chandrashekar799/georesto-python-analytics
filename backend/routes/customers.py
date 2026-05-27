from fastapi import APIRouter, Query
from backend.services.data_mgr import get_customers as fetch_customers, load_all_customers
import time

router = APIRouter()


# ================= 👥 CUSTOMERS =================
@router.get("/customers")
async def get_customers(
    segment: str = Query("All"),
    max_distance: float = Query(None),
    min_dist: float = Query(0)
):
    try:
        print(" /customers API called")

        df = fetch_customers(
            min_distance=min_dist,
            max_distance=max_distance,
            segment=segment
        )

        if df.empty:
            return []

        # ✅ INCLUDE visits
        cols = [
            col for col in
            ["customer_id", "lat", "lng", "visits", "segment", "distance"]
            if col in df.columns
        ]

        return df[cols].to_dict(orient="records")

    except Exception as e:
        print(" Customers API error:", e)
        return []
# ================= 📊 DASHBOARD =================
@router.get("/dashboard")
async def get_dashboard_stats():
    print(" /dashboard API called")

    start_time = time.time()

    try:
        # ✅ Use SAME cached dataset
        df = load_all_customers()

        if df.empty:
            return {
                "total_customers": 0,
                "nearby": 0,
                "frequent": 0,
                "restaurants": []
            }

        # ⚡ Fast stats (no recalculation)
        customers_data = {
            "total_customers": len(df),
            "nearby": int((df["distance"] <= 5).sum()),  # km
            "frequent": int((df["segment"] == "Frequent").sum())
        }

    except Exception as e:
        print(" Customer stats error:", e)
        customers_data = {
            "total_customers": 0,
            "nearby": 0,
            "frequent": 0
        }

    # ================= 🏨 RESTAURANTS =================
    try:
        # 🔥 This is fine (small dataset)
        from backend.db.supabase_client import supabase

        res = supabase.table("restaurants").select("name, lat, lng").execute()
        restaurants = res.data if res.data else []

    except Exception as e:
        print(" Restaurant fetch error:", e)
        restaurants = []

    print(f" Dashboard API time: {round(time.time() - start_time, 2)} sec")

    return {
        **customers_data,
        "restaurants": restaurants
    }