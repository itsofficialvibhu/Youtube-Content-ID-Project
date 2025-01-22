from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict
import os
import uuid
from pydantic import BaseModel
from pathlib import Path
import hashlib
import sqlite3
import subprocess

# Initialize FastAPI app
app = FastAPI()

# Database connection
DATABASE = "content_id.db"
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fingerprints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id TEXT UNIQUE,
        file_path TEXT,
        fingerprint TEXT,
        owner TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT,
        owner TEXT,
        policy TEXT,
        regions TEXT,
        match_details TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Directory to store uploaded files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Model for claim policies
class ClaimPolicy(BaseModel):
    policy: str
    regions: List[str]
    owner: str

# Utility functions
def generate_fingerprint(file_path: str) -> str:
    """Generate a fingerprint for the given audio/video file."""
    # Use FFmpeg to extract audio and hash it
    temp_audio = f"{file_path}.wav"
    try:
        subprocess.run(
            ["ffmpeg", "-i", file_path, "-ar", "22050", "-ac", "1", temp_audio],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        with open(temp_audio, "rb") as f:
            content = f.read()
            fingerprint = hashlib.sha256(content).hexdigest()
    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
    return fingerprint

def store_fingerprint(file_id: str, file_path: str, fingerprint: str, owner: str):
    """Store fingerprint and metadata in the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO fingerprints (file_id, file_path, fingerprint, owner) VALUES (?, ?, ?, ?)",
        (file_id, file_path, fingerprint, owner),
    )
    conn.commit()
    conn.close()

def check_fingerprint(fingerprint: str) -> Dict:
    """Check if the fingerprint exists in the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM fingerprints WHERE fingerprint = ?", (fingerprint,)
    )
    match = cursor.fetchone()
    conn.close()
    if match:
        return {
            "file_id": match[1],
            "file_path": match[2],
            "owner": match[4]
        }
    return {}

# API Endpoints
@app.post("/upload")
async def upload_file(file: UploadFile, owner: str):
    """Upload a new file and store its fingerprint."""
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Generate fingerprint
    fingerprint = generate_fingerprint(str(file_path))

    # Check for matches
    match = check_fingerprint(fingerprint)
    if match:
        return JSONResponse(
            {
                "message": "Content match found!",

                "match": match,
            },
            status_code=200,
        )

    # Store fingerprint if no match
    store_fingerprint(file_id, str(file_path), fingerprint, owner)
    return {"message": "File uploaded successfully.", "file_id": file_id}

@app.post("/claim")
async def create_claim(video_id: str, claim_policy: ClaimPolicy):
    """Create a claim on a video based on matching content."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO claims (video_id, owner, policy, regions, match_details) VALUES (?, ?, ?, ?, ?)",
        (
            video_id,
            claim_policy.owner,
            claim_policy.policy,
            ",".join(claim_policy.regions),
            "Matched Content ID",  # Placeholder for match details
        ),
    )
    conn.commit()
    conn.close()
    return {"message": "Claim created successfully."}

@app.get("/claims/{video_id}")
async def get_claims(video_id: str):
    """Retrieve all claims for a given video ID."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM claims WHERE video_id = ?", (video_id,))
    claims = cursor.fetchall()
    conn.close()
    return {"claims": claims}

@app.get("/videos")
async def list_videos():
    """List all stored videos and their metadata."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fingerprints")
    videos = cursor.fetchall()
    conn.close()
    return {"videos": videos}