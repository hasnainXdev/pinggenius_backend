# Quickstart Guide: Enhanced Profile Analysis and Outreach Generation

## Overview
This guide will help you set up and start using the enhanced profile analysis and outreach generation feature with validation guards and improved quality controls.

## Prerequisites
- Python 3.11+
- Poetry or pip for dependency management
- MongoDB instance running locally or remotely
- OpenAI API key

## Setup

### 1. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Update the .env file with your configuration
# - MONGO_URL: Your MongoDB connection string
# - OPENAI_API_KEY: Your OpenAI API key
# - Any other required environment variables
```

### 2. Install Dependencies
```bash
# Using poetry
poetry install

# Or using pip with requirements.txt
pip install -r requirements.txt
```

### 3. Run Database Migrations (if applicable)
```bash
# If you have any database migrations to run
python -m scripts.migrate
```

## Running the Application

### Development Mode
```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using the Makefile if available
make dev
```

### Production Mode
```bash
# Using uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# Or using gunicorn for production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Usage Examples

### 1. Profile Analysis with Validation Guards
```bash
curl -X POST http://localhost:8000/profile/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.linkedin.com/in/example-profile",
    "role": "Software Engineer",
    "company": "Tech Corp",
    "industry": "Software",
    "tone": "FRIENDLY"
  }'
```

**Successful Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "url": "https://www.linkedin.com/in/example-profile",
  "role": "Software Engineer",
  "company": "Tech Corp",
  "industry": "Software",
  "recent_activity": "Posted about new project launch",
  "pain_point_inferred": "Scaling team productivity"
}
```

**Validation Error Response:**
```json
{
  "error": "Validation failed",
  "message": "Profile missing required fields: role is required, and either company or industry is required",
  "actionable_alternative": "Please provide role, and either company or industry information"
}
```

### 2. Outreach Generation with Enhanced Quality Controls
```bash
curl -X POST http://localhost:8000/outreach/generate \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "507f1f77bcf86cd799439011",
    "tone": "FRIENDLY"
  }'
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439012",
  "profile_id": "507f1f77bcf86cd799439011",
  "connection_note": "Hi, I noticed your recent post about the new project launch...",
  "dm_1": "Following up on our connection. I saw you're working on scaling challenges...",
  "follow_up_1": "Did you get a chance to review the resources I shared?",
  "follow_up_2": "Just checking in to see if there's interest in discussing solutions.",
  "tone": "FRIENDLY",
  "created_at": "2023-10-20T10:00:00Z",
  "updated_at": "2023-10-20T10:05:00Z"
}
```

### 3. Sequence Refinement with Tone Validation
```bash
curl -X POST http://localhost:8000/outreach/refine \
  -H "Content-Type: application/json" \
  -d '{
    "sequence_id": "507f1f77bcf86cd799439012",
    "message_position": 2,
    "feedback": "Make it more professional",
    "tone": "AUTHORITY"
  }'
```

## Key Features Explained

### 1. Profile Validation Guards
The system validates that incoming profiles have sufficient context before processing:
- Role field is required
- Either company or industry field is required
- If validation fails, a safe fallback message is returned instead of generating hallucinated content

### 2. Pain Point Inference
The system uses a curated list of role/industry-specific pain points to improve outreach effectiveness:
- Maps roles like "Software Engineer" to relevant pain points like "Scaling team productivity"
- Incorporates these pain points into the generated outreach messages

### 3. Sequence Cohesion
Maintains context between messages in a sequence:
- Temporary storage during generation for performance
- Option to persist valuable sequences permanently
- Follow-up messages reference content from previous messages

### 4. Tone Consistency Validation
Ensures generated messages adhere to requested tone parameters:
- Prescriptive rules for each tone (e.g., Friendly → max 1 emoji, Authority → no slang)
- Regenerates messages that violate tone requirements

### 5. Timeout Protection
Implements 8-second timeout to prevent hanging requests:
- Prevents queue pileups
- Ensures predictable API behavior
- Returns appropriate timeout response when exceeded

### 6. Idempotency Protection
Prevents duplicate charges for identical requests:
- Uses request-based keys combining profile data and parameters
- Returns cached results for duplicate requests
- Maintains consistency across repeated requests

## Testing

### Running Unit Tests
```bash
# Run all tests
pytest

# Run tests for specific module
pytest tests/unit/test_profile_validation.py

# Run tests with coverage
pytest --cov=services --cov=models --cov-report=html
```

### Running Integration Tests
```bash
# Run integration tests
pytest tests/integration/
```

## Troubleshooting

### Common Issues

1. **Profile validation failing unexpectedly**
   - Ensure you're providing both role and either company or industry
   - Check that the fields are not empty strings

2. **Timeout errors during outreach generation**
   - This is expected behavior when LLM processing takes too long
   - The system will return a timeout response after 8 seconds
   - Retry the request if needed

3. **Tone validation rejecting generated messages**
   - The system regenerates messages that don't match the requested tone
   - If consistently failing, review the tone requirements in the configuration

### Logging
Check the application logs for detailed error information:
```bash
# View logs
tail -f logs/app.log

# Or if using Docker
docker logs pinggenius-backend
```

## Next Steps
- Explore the API documentation at `/docs` endpoint
- Review the data models in the `models/` directory
- Check out the service implementations in the `services/` directory
- Look at the test suite for usage examples