# GeoResto Python Analytics

A 100% Python-based Geo-Analytics Web Application for restaurant customer segmentation and proximity analysis.

## Setup Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python runner.py
   ```

## Project Structure

- `backend/`: FastAPI application for data management and geo-calculations.
- `frontend/`: Streamlit dashboard for visualization.
- `data/`: CSV data storage.
- `runner.py`: Orchestrates both backend and frontend services.

## API Endpoints

- `GET /api/customers`: Returns all customers.
- `GET /api/customers/segmented?segment=New`: Filters customers by segment.
- `GET /api/customers/nearby?lat=...&lng=...&radius=...`: Returns customers within a specific radius (meters).
