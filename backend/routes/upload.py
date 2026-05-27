from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import hashlib
import io
from backend.db.supabase_client import supabase

router = APIRouter()


# ✅ Generate file hash (for duplicate detection)
def generate_file_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()


@router.post("/upload-customers")
async def upload_customers(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # ================= 🔥 STEP 1: FILE HASH =================
        file_hash = generate_file_hash(contents)

        existing = supabase.table("uploads") \
            .select("id") \
            .eq("file_hash", file_hash) \
            .execute()

        # ✅ SAFE DELETE (NO UUID ERROR)
        if existing.data:
            supabase.table("customers").delete().neq("customer_id", "").execute()

        # ================= 📄 STEP 2: READ CSV =================
        df = pd.read_csv(io.BytesIO(contents))

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail=" CSV is empty"
            )

        # ================= 🧹 STEP 3: CLEAN DATA =================
        df.columns = df.columns.str.strip().str.lower()

        # Rename columns safely
        df.rename(columns={
            "customer id": "customer_id",
            "latitude": "lat",
            "longitude": "lng"
        }, inplace=True)

        # ✅ REMOVE ANY 'id' COLUMN (CRITICAL FIX)
        df = df.loc[:, [col for col in df.columns if col.lower() != "id"]]

        # ✅ REQUIRED COLUMNS CHECK
        required_cols = ["customer_id", "lat", "lng"]
        for col in required_cols:
            if col not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required column: {col}"
                )

        # ================= 🔄 TYPE CONVERSION =================
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lng"] = pd.to_numeric(df["lng"], errors="coerce")

        df["distance"] = pd.to_numeric(
            df.get("distance", 0), errors="coerce"
        ).fillna(0)

        df["visits"] = pd.to_numeric(
            df.get("visits", 1), errors="coerce"
        ).fillna(1).astype(int)

        # ✅ DROP INVALID ROWS
        df = df.dropna(subset=["customer_id", "lat", "lng"])

        # Convert to dict
        data = df.to_dict(orient="records")

        # ================= 📦 STEP 4: BATCH INSERT =================
        batch_size = 100
        inserted = 0

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]

            clean_batch = []

            for row in batch:
                try:
                    clean_row = {
                        "customer_id": str(row.get("customer_id")).strip(),
                        "lat": float(row.get("lat")),
                        "lng": float(row.get("lng")),
                        "distance": float(row.get("distance", 0)),
                        "visits": int(row.get("visits", 1))
                    }

                    # 🚫 skip bad rows
                    if not clean_row["customer_id"]:
                        continue

                    clean_batch.append(clean_row)

                except:
                    continue

            if not clean_batch:
                continue

            print("Sample Row:", clean_batch[0])

            response = supabase.table("customers").insert(clean_batch).execute()

            if hasattr(response, "error") and response.error:
                raise HTTPException(
                    status_code=500,
                    detail=str(response.error)
                )

            inserted += len(clean_batch)

        # ================= 🧾 STEP 5: STORE UPLOAD HISTORY =================
        supabase.table("uploads").upsert(
            {
                "file_name": file.filename,
                "file_hash": file_hash,
                "row_count": inserted
            },
            on_conflict="file_hash"   # 🔥 THIS IS THE FIX
        ).execute()

        # ================= ✅ STEP 6: RESPONSE =================
        return {
            "status": "success",
            "message": "Upload successful",
            "rows_uploaded": inserted
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )