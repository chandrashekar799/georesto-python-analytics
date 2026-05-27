import os

# ✅ FIXED (no /api here)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Default Map Center (fallback)
CENTER_LAT = 12.9716
CENTER_LNG = 77.5946

# Map Settings
DEFAULT_ZOOM = 12

# Limits
MAX_POINTS = 2000