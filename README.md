# Career Radar — Skill-Based Job Recommendation System

A college mini project that recommends career roles from a user's skills using a content-based recommendation approach.

## Stack

- Python
- Pandas
- NumPy
- scikit-learn
- FastAPI
- HTML
- CSS
- JavaScript

## Architecture

Browser → JavaScript fetch() → FastAPI → Recommendation Engine → CSV dataset → JSON → Browser

## Recommendation method

The recommendation engine:

1. Loads jobs from `data/jobs.csv`.
2. Uses TF-IDF to represent job skill text numerically.
3. Converts the user's skills into the same vector space.
4. Calculates cosine similarity between the user and every job.
5. Adds a direct skill-coverage signal.
6. Sorts jobs by the resulting match percentage.

## Run locally

### 1. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install packages

```bash
pip install -r requirements.txt
```

### 3. Start the API

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API runs at:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### 4. Open the frontend

Open `frontend/index.html` in your browser.

For a smoother local setup, VS Code's Live Server extension can serve the frontend.

## Project structure

```text
skill-job-recommender/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   └── recommender.py
├── data/
│   └── jobs.csv
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── tests/
│   └── test_recommender.py
├── requirements.txt
└── README.md
```
