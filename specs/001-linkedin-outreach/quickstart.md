# Quickstart Guide: LinkedIn Outreach Generation

## Overview
This guide provides a quick introduction to setting up and using the LinkedIn Outreach Generation feature. It covers the essential steps to get the service running and start generating personalized LinkedIn outreach sequences.

## Prerequisites
- Python 3.11+
- MongoDB instance (local or cloud)
- Access to Gemini API
- Apify account for LinkedIn data extraction

## Setup

### 1. Environment Configuration
```bash
# Clone the repository
git clone <repository-url>
cd pinggenius_backend_fastapi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the project root with the following variables:

```env
MONGODB_URL=mongodb://localhost:27017/pinggenius
GEMINI_API_KEY=your_gemini_api_key
APIFY_API_KEY=your_apify_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 3. Database Setup
Ensure MongoDB is running and accessible at the configured URL. The application will automatically create required collections on first run.

## Running the Service

### Development
```bash
# Run the FastAPI application
uvicorn main:app --reload --port 8000
```

### Production
```bash
# Using gunicorn for production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Usage

### 1. Profile Analysis
Analyze a LinkedIn profile to extract context for outreach generation:

```bash
curl -X POST "http://localhost:8000/profile/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.linkedin.com/in/example-profile"
  }'
```

Expected response:
```json
{
  "id": "507f1f77bcf86cd799439011",
  "url": "https://www.linkedin.com/in/example-profile",
  "role": "Software Engineer",
  "company": "Tech Corp",
  "industry": "Technology",
  "recent_activity": "Published article on AI",
  "created_at": "2023-10-05T14:48:00.000Z",
  "updated_at": "2023-10-05T14:48:00.000Z"
}
```

### 2. Outreach Generation
Generate a complete outreach sequence based on the analyzed profile:

```bash
curl -X POST "http://localhost:8000/outreach/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "507f1f77bcf86cd799439011",
    "tone": "Friendly"
  }'
```

Expected response:
```json
{
  "id": "507f1f77bcf86cd799439012",
  "profile_id": "507f1f77bcf86cd799439011",
  "connection_note": "Hi there! I noticed your recent article on AI...",
  "dm_1": "Following up on my connection request...",
  "follow_up_1": "Hope you had a chance to read my previous message...",
  "follow_up_2": "Last follow-up on this topic...",
  "tone": "Friendly",
  "created_at": "2023-10-05T14:49:00.000Z",
  "updated_at": "2023-10-05T14:49:00.000Z"
}
```

### 3. Message Refinement
Refine specific messages in an existing sequence:

```bash
curl -X POST "http://localhost:8000/outreach/refine" \
  -H "Content-Type: application/json" \
  -d '{
    "sequence_id": "507f1f77bcf86cd799439012",
    "message_position": 2,
    "feedback": "Make the message more professional",
    "tone": "Authority"
  }'
```

### 4. Retrieve Sequence
Get an existing outreach sequence by ID:

```bash
curl -X GET "http://localhost:8000/sequences/507f1f77bcf86cd799439012"
```

## Error Handling
The API follows standard HTTP status codes:
- 200: Success
- 400: Bad request (invalid parameters)
- 404: Resource not found
- 500: Internal server error

## Testing
Run the test suite to verify the service is working correctly:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_outreach.py
```

## Troubleshooting
- If profile analysis fails, verify the LinkedIn URL is valid and publicly accessible
- If message generation is slow, check your Gemini API key and rate limits
- For database connection issues, verify MongoDB is running and accessible