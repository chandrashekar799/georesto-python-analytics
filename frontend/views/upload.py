import streamlit as st
import pandas as pd
import requests
from config import BACKEND_URL


def show():

    st.title("Data Upload")

    # ✅ SESSION STATE FOR SUCCESS MESSAGE
    if "upload_success" not in st.session_state:
        st.session_state.upload_success = None

    # ✅ SHOW SUCCESS MESSAGE (AFTER RELOAD)
    if st.session_state.upload_success:
        st.success(st.session_state.upload_success)

    # ================= 🏨 RESTAURANT UPLOAD =================
    st.subheader("🏨 Upload Restaurants")

    st.info("CSV format: name, lat, lng")
    st.warning("Uploading the same file again will be blocked")

    rest_file = st.file_uploader("Upload Restaurants CSV", type=["csv"], key="rest")

    if rest_file:
        try:
            rest_df = pd.read_csv(rest_file)

            st.success("Restaurant file loaded")
            st.dataframe(rest_df.head(), use_container_width=True)

            if st.button("Upload Restaurants"):

                progress = st.progress(0)
                status_text = st.empty()

                try:
                    status_text.text("Preparing upload...")
                    progress.progress(10)

                    files = {
                        "file": (rest_file.name, rest_file.getvalue(), "text/csv")
                    }

                    status_text.text("Sending to server...")
                    progress.progress(40)

                    res = requests.post(
                        f"{BACKEND_URL}/api/upload-restaurants",
                        files=files,
                        timeout=60
                    )

                    progress.progress(80)
                    status_text.text("Processing response...")

                    if res.status_code == 200:
                        response = res.json()
                        rows = response.get("rows_uploaded", 0)

                        progress.progress(100)
                        status_text.text("Upload complete!")

                        # ✅ STORE SUCCESS MESSAGE
                        st.session_state.upload_success = f"✅ Upload successful! ({rows} restaurants)"
                        st.balloons()

                    else:
                        try:
                            error_msg = res.json().get("detail", res.text)
                        except:
                            error_msg = res.text

                        progress.progress(100)
                        status_text.text("Upload failed")
                        st.error(error_msg)

                except Exception as e:
                    progress.progress(100)
                    status_text.text("Upload failed")
                    st.error(f"Error: {e}")

        except Exception as e:
            st.error(f"Invalid restaurant CSV: {e}")

    st.divider()

    # ================= 👥 CUSTOMER UPLOAD =================
    st.subheader("Upload Customers")

    st.info(
        "CSV should contain: customer_id, lat, lng\n"
        "Optional: distance, visits"
    )
    st.warning("Uploading the same file again will be blocked")

    file = st.file_uploader("Upload Customers CSV", type=["csv"], key="cust")

    if file:
        try:
            df = pd.read_csv(file)

            st.success("File loaded successfully")
            st.dataframe(df.head(), use_container_width=True)

            # ================= CLEAN COLUMN NAMES =================
            df.columns = [col.lower().strip() for col in df.columns]

            # ================= AUTO COLUMN MAPPING =================
            column_mapping = {
                "latitude": "lat",
                "longitude": "lng",
                "long": "lng",
                "geo_lat": "lat",
                "geo_lng": "lng",
                "ad_id": "customer_id"
            }

            for old, new in column_mapping.items():
                if old in df.columns:
                    df.rename(columns={old: new}, inplace=True)

            # ================= REQUIRED CHECK =================
            required_cols = ["lat", "lng"]
            missing = [c for c in required_cols if c not in df.columns]

            if missing:
                st.error(f"Missing required columns: {missing}")
                return

            # ================= TYPE FIX =================
            df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
            df["lng"] = pd.to_numeric(df["lng"], errors="coerce")

            df = df.dropna(subset=["lat", "lng"])

            if df.empty:
                st.error("No valid data after cleaning")
                return

            st.success(f"Cleaned Data Ready ({len(df)} rows)")

            # ================= SESSION STORAGE =================
            st.session_state.data = df
            st.session_state.data_loaded = True

            st.success("Data is now available in Dashboard")

            if st.button("Upload Customers"):

                progress = st.progress(0)
                status_text = st.empty()

                try:
                    status_text.text("Preparing upload...")
                    progress.progress(10)

                    files = {
                        "file": (file.name, file.getvalue(), "text/csv")
                    }

                    status_text.text("Sending to server...")
                    progress.progress(40)

                    res = requests.post(
                        f"{BACKEND_URL}/api/upload-customers",
                        files=files,
                        timeout=60
                    )

                    progress.progress(80)
                    status_text.text("Processing response...")

                    if res.status_code == 200:
                        response = res.json()
                        rows = response.get("rows_uploaded", 0)

                        progress.progress(100)
                        status_text.text("Upload complete!")

                        # ✅ STORE SUCCESS MESSAGE
                        st.session_state.upload_success = f"✅ Upload successful! ({rows} customers)"
                        st.balloons()

                    else:
                        try:
                            error_msg = res.json().get("detail", res.text)
                        except:
                            error_msg = res.text

                        progress.progress(100)
                        status_text.text("Upload failed")
                        st.error(f"Upload failed: {error_msg}")

                except Exception as e:
                    progress.progress(100)
                    status_text.text("Upload failed")
                    st.error(f"Server error: {e}")

        except Exception as e:
            st.error(f"Invalid CSV file: {e}")