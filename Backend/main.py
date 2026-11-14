import hashlib
import hmac
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="Local events API",
    description="A small JSON serving local community events.",
    version="1.0.0",
)

# Allowing the frontend to call the API
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/")
def root() -> dict:
    """A friendly landing page pointing at the docs/endpoints."""
    return {
        "name": "Local events API",
        "docs": "/docs",
        "endpoints": [
            "/events",
            "/events/{event_id}",
            "/events/{event_id}/save",
            "/auth/register",
            "/auth/login",
            "/health",
        ],
    }


@app.get("/health")
def health() -> dict:
    """Trivial "is the service up?" endpoint for health checks."""
    return {"status": "ok"}


# ---------- Events ----------
class Event(BaseModel):
    id: str
    title: str
    category: str
    location: str
    date: str
    time: str
    summary: str
    description: str
    saved: bool = Field(default=False, description="Whether the event is bookmarked or not.")


DATA_FILE = Path(__file__).resolve().parent / "data" / "events.json"
EVENTS: list[dict] = json.loads(DATA_FILE.read_text(encoding="utf-8"))


@app.get("/events", response_model=list[Event])
def list_events(
    category: str | None = Query(None, description="Filter category by name"),
    saved: bool | None = Query(None, description="Filter by saved status"),
) -> list[dict]:
    events = EVENTS
    if category:
        events = [e for e in events if e["category"].lower() == category.lower()]
    if saved is not None:
        events = [e for e in events if e["saved"] == saved]
    return events


def find_event_or_404(event_id: str) -> dict:
    for event in EVENTS:
        if event["id"] == event_id:
            return event
    raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found.")


@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str) -> dict:
    return find_event_or_404(event_id)


@app.post("/events/{event_id}/save", response_model=Event)
def save_event(event_id: str) -> dict:
    event = find_event_or_404(event_id)
    event["saved"] = True
    return event


@app.delete("/events/{event_id}/save", response_model=Event)
def unsave_event(event_id: str) -> dict:
    event = find_event_or_404(event_id)
    event["saved"] = False
    return event


# ---------- Users ----------
ITERATIONS = 200_000


class UserCredentials(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=6, description="Plain text password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        candidate = value.strip().lower()
        if "@" not in candidate or "." not in candidate.split("@")[-1]:
            raise ValueError("Must be a valid email address")
        return candidate


class UserPublic(BaseModel):
    email: str


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, digest_hex = stored_hash.split("$")
        salt = bytes.fromhex(salt_hex)
        digest = bytes.fromhex(digest_hex)
    except (ValueError, AttributeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return hmac.compare_digest(actual, digest)


USERS: dict[str, str] = {}  # email -> password hash


@app.post("/auth/register", response_model=UserPublic, status_code=201)
def register_user(credentials: UserCredentials) -> UserPublic:
    if credentials.email in USERS:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    USERS[credentials.email] = hash_password(credentials.password)
    return UserPublic(email=credentials.email)


@app.post("/auth/login", response_model=UserPublic)
def login_user(credentials: UserCredentials) -> UserPublic:
    stored = USERS.get(credentials.email)
    if stored is None or not verify_password(credentials.password, stored):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return UserPublic(email=credentials.email)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on the server."},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
