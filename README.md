# Content ID System

This is a simplified Content ID system inspired by YouTube's Content ID functionality. It allows copyright owners to upload their content, generate unique fingerprints for detection, and manage claims on matching uploaded videos.

---

## Features
1. Upload files (audio/video) and generate unique fingerprints for each.
2. Automatically detect matching files in the database.
3. Manage claims (monetize, block, or track) based on matches.
4. Store metadata and manage uploaded files securely.

---

## Project Structure


---

## Installation Instructions

### Prerequisites
- Python 3.8 or higher
- FFmpeg installed and added to your system's PATH.

### Steps to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/itsofficialvibhu/content-id-project.git
   cd content-id-project

 ### Install dependencies:
pip install -r requirements.txt

 ### Start the application:
 uvicorn app:app --reload

Access the API at: http://127.0.0.1:8000/docs

### API Endpoints
1. Upload File
Endpoint: /upload
Method: POST
Description: Upload a file, generate a fingerprint, and check for matches.
Parameters:
file: The file to upload (audio/video).
owner: Name of the content owner.

Create Claim
Endpoint: /claim
Method: POST
Description: Create a claim on a video based on matching content.
Payload:
{
  "video_id": "<video_id>",
  "policy": "monetize",
  "regions": ["US", "EU"],
  "owner": "OwnerName"
}

 Get Claims
Endpoint: /claims/{video_id}
Method: GET
Description: Retrieve claims for a specific video.

List All Videos
Endpoint: /videos
Method: GET
Description: View all uploaded videos and their metadata.

