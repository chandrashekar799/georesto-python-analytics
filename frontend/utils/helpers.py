import streamlit as st


# ================= DISTANCE CONVERTER =================
@st.cache_data(ttl=3600)
def convert_to_meters(value):
    """
    Converts:
    - '5 km' → 5000
    - '200 m' → 200
    - '2.5km' → 2500
    - '500M' → 500

    Returns:
    - float (meters)
    - None if invalid
    """

    try:
        if value is None:
            return None

        value = str(value).lower().strip()

        if value == "":
            return None

        # Remove spaces (important fix)
        value = value.replace(" ", "")

        # KM conversion
        if "km" in value:
            num = float(value.replace("km", ""))
            return num * 1000

        # Meter conversion
        elif "m" in value:
            num = float(value.replace("m", ""))
            return num

        # Direct number (assume meters)
        return float(value)

    except Exception as e:
        print("convert_to_meters error:", e)
        return None