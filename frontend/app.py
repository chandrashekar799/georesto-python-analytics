import streamlit as st

# ✅ FIRST LINE
st.set_page_config(page_title="GeoResto Dashboard", layout="wide")

import os
from views import dashboard, analytics, upload, campaigns


# ================= CSS (CACHE) =================
@st.cache_data
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    with open(css_path) as f:
        return f.read()


st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)


# ================= SESSION STATE INIT =================
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ================= SIDEBAR =================
st.sidebar.title("GeoResto")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Analytics", "Campaigns", "Data Upload"],
    index=["Dashboard", "Analytics", "Campaigns", "Data Upload"].index(st.session_state.page)
)

st.session_state.page = menu


# ================= ROUTING =================
if menu == "Dashboard":
    dashboard.show()

elif menu == "Analytics":
    analytics.show()

elif menu == "Campaigns":
    campaigns.show()

elif menu == "Data Upload":
    upload.show()