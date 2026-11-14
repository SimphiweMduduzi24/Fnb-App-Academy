# Community Events App

A Flet (Python) app for browsing local community events, backed by a FastAPI REST API.

## Features
- Sign up and log in
- Browse events and filter by category (Music, Markets, Sports, Community)
- View full event details (date, time, location, description)
- Save and unsave events, and view them under "Saved"

## Tech stack
- **Frontend:** Flet
- **Backend:** FastAPI, Uvicorn
- **HTTP client:** httpx
- **Data:** events stored in `Backend/data/events.json`

## How to run
1. Install the requirements: `pip install -r requirements.txt`
2. Start the backend:
   cd Backend
   python main.py
3. In a second terminal, start the app:
   cd Frontend
   python src/main.py

The backend must be running before you open the app.

## Notes
Accounts and saved events are kept in memory, so they reset when the backend restarts.
