# PingGenius LinkedIn Outreach API Documentation

## Overview
The PingGenius LinkedIn Outreach API enables users to generate personalized LinkedIn outreach sequences based on profile analysis. The system extracts context from LinkedIn profiles and generates tailored messages that are appropriate for the platform.

## API Endpoints

### Profile Analysis
- **POST /profile/analyze**
  - Analyze a LinkedIn profile and extract context for message generation
  - Request body: `{"url": "https://www.linkedin.com/in/username"}`
  - Response: Profile information including role, company, industry, and recent activity

### Outreach Generation
- **POST /outreach/generate**
  - Generate a complete LinkedIn outreach sequence based on profile context
  - Request body: `{"profile_id": "profile_id", "tone": "Friendly"}` (tone options: Friendly, Direct, Authority, Casual)
  - Response: Complete outreach sequence with connection note, DMs, and follow-ups

### Message Refinement
- **POST /outreach/refine**
  - Refine a specific message in an existing sequence based on feedback
  - Request body: `{"sequence_id": "sequence_id", "message_position": 2, "feedback": "Make it more professional", "tone": "Authority"}`
  - Response: Updated outreach sequence with refined message

### Sequence Retrieval
- **GET /outreach/{sequence_id}**
  - Retrieve an existing outreach sequence by ID
  - Response: The complete outreach sequence

## Architecture

### Components
- **API Layer**: FastAPI endpoints in `/api/`
- **Service Layer**: Business logic in `/services/`
- **Data Layer**: Models in `/models/` and database utilities in `/database/`
- **Utilities**: Common utilities in `/utils/`

### Data Flow
1. User submits LinkedIn profile URL
2. Profile service analyzes the profile and extracts context
3. Context extractor prepares information for message generation
4. Sequence generator creates personalized outreach sequence using OpenAI Agents
5. Generated sequence is stored in MongoDB and returned to user

## Configuration
- Environment variables in `.env` file
- Settings managed in `/config/settings.py`
- Database connection in `/database/mongo.py`

## Security & Privacy
- GDPR compliant data handling
- Automatic data cleanup after retention period
- Rate limiting to prevent abuse
- Secure API endpoints

## Error Handling
- Comprehensive error messages with actionable alternatives
- Retry logic with exponential backoff for external service calls
- Proper HTTP status codes for all responses

## Development

### Running the Application
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Environment Variables
- `MONGODB_URL`: MongoDB connection string
- `GEMINI_API_KEY`: OpenAI API key for message generation
- `APIFY_API_KEY`: Apify API key for LinkedIn profile scraping
- `REQUESTS_PER_MINUTE`: Rate limit for API endpoints