# GeoResto Python Analytics

A full-stack restaurant analytics and geo-intelligence dashboard built using Python.
This project helps analyze restaurant data, customer insights, location-based analytics, and campaign performance through an interactive dashboard.

---

## Features

* Restaurant analytics dashboard
* Customer data analysis
* Geo-location based insights
* Campaign performance tracking
* Data upload and processing
* Interactive frontend views
* REST API backend services
* Clean modular project structure

---

## Tech Stack

### Backend

* Python
* FastAPI
* Supabase
* REST APIs

### Frontend

* Python
* Streamlit
* Custom CSS

### Database

* Supabase PostgreSQL

---

## Project Structure

```bash
georesto-python-analytics/
│
├── backend/
│   ├── db/
│   ├── routes/
│   ├── services/
│   └── main.py
│
├── frontend/
│   ├── services/
│   ├── utils/
│   ├── views/
│   └── app.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/chandrashekar799/georesto-python-analytics.git
```

Move into the project folder:

```bash
cd georesto-python-analytics
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Run Backend

```bash
uvicorn backend.main:app --reload
```

Backend runs on:

```bash
http://127.0.0.1:8000
```

---

## Run Frontend

```bash
streamlit run frontend/app.py
```

Frontend runs on:

```bash
http://localhost:8501
```

---

## Modules

### Dashboard

Displays analytics and business insights.

### Campaigns

Tracks marketing campaign performance.

### Upload

Upload and process restaurant/customer datasets.

### Analytics

Generates customer and geo-based analytical reports.

---

## Future Improvements

* AI-based recommendations
* Real-time analytics
* Advanced visualization charts
* User authentication
* Cloud deployment

---

## Author

Chandrashekar

GitHub:

[chandrashekar799 GitHub Profile](https://github.com/chandrashekar799?utm_source=chatgpt.com)
