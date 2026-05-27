from fastapi import APIRouter, UploadFile, File
import pandas as pd
import io
import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


# ================= 🏨 UPLOAD RESTAURANTS =================
@router.post("/upload-restaurants")
async def upload_restaurants(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        if df.empty:
            return {"status": "error", "message": "CSV is empty"}

        df.columns = df.columns.str.strip().str.lower()

        required_cols = ["name", "lat", "lng"]
        missing = [c for c in required_cols if c not in df.columns]

        if missing:
            return {"status": "error", "message": f"Missing columns: {missing}"}

        # Clean data
        df = df.drop(columns=["id", "created_at"], errors="ignore")
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
        df = df.dropna(subset=["lat", "lng"])

        if df.empty:
            return {"status": "error", "message": "No valid lat/lng data"}

        data = df.to_dict(orient="records")

        url = f"{SUPABASE_URL}/rest/v1/restaurants"

        # 🔁 Retry logic
        for i in range(3):
            try:
                res = requests.post(url, headers=HEADERS, json=data, timeout=10)

                if res.status_code in [200, 201]:
                    return {
                        "status": "success",
                        "restaurants_uploaded": len(data)
                    }
                else:
                    print(" Upload error:", res.text)

            except Exception as e:
                print(f" Upload retry {i+1} failed:", e)
                time.sleep(2)

        return {"status": "error", "message": "Upload failed after retries"}

    except Exception as e:
        print(" Upload restaurants error:", e)
        return {"status": "error", "message": str(e)}


# ================= 📊 GET RESTAURANTS =================
@router.get("/restaurants")
async def get_restaurants():
    url = f"{SUPABASE_URL}/rest/v1/restaurants?select=id,name,lat,lng"

    for i in range(3):
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)

            if res.status_code == 200:
                return res.json()
            else:
                print(" Fetch error:", res.text)

        except Exception as e:
            print(f" Fetch retry {i+1} failed:", e)
            time.sleep(2)

    return []