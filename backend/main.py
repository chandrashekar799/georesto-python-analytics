from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import customers, upload, restaurants
import random
import asyncio

app = FastAPI(title="GeoResto API")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ROUTERS =================
app.include_router(customers.router, prefix="/api")
app.include_router(upload.router, prefix="/api")        # ✅ FIXED
app.include_router(restaurants.router, prefix="/api")   # ✅ FIXED

# ================= ROOT =================
@app.get("/")
async def root():
    return {"message": "GeoResto Backend is running"}

# ================= HEALTH =================
@app.get("/api/health")
def health():
    return {"status": "ok"}


# ================= LIVE TRACKING =================
live_customers = [
    {
        "customer_id": i,
        "lat": 12.97 + random.uniform(-0.01, 0.01),
        "lng": 77.59 + random.uniform(-0.01, 0.01),
    }
    for i in range(50)
]

@app.get("/api/live-customers")
def get_live_customers():
    for c in live_customers:
        c["lat"] += random.uniform(-0.0005, 0.0005)
        c["lng"] += random.uniform(-0.0005, 0.0005)

    return {"data": live_customers}


@app.websocket("/ws/live")
async def websocket_live(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            for c in live_customers:
                c["lat"] += random.uniform(-0.0005, 0.0005)
                c["lng"] += random.uniform(-0.0005, 0.0005)

            await ws.send_json(live_customers)
            await asyncio.sleep(1)

    except:
        print("WebSocket Adisconnected")