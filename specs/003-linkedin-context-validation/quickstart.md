# Quickstart Guide: LinkedIn Context Validation

## Overview
This guide will help you quickly set up and use the LinkedIn context validation feature. This feature validates LinkedIn profiles to ensure sufficient context exists before generating outreach messages, improving reply-worthiness predictability.

## Prerequisites
- Python 3.11+
- MongoDB instance running
- Environment variables configured (see `.env.example`)

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Set up your `.env` file with the required configurations:
```bash
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=pinggenius
GEMINI_API_KEY=your_api_key_here
```

### 3. Run Database Migrations
```bash
# Apply any necessary database migrations
python -m database.migrate
```

## Usage

### 1. Validate LinkedIn Profile Context
Send a POST request to validate a LinkedIn profile:

```bash
curl -X POST http://localhost:8000/linkedin/context/validate \
  -H "Content-Type: application/json" \
  -d '{
    "profile_url": "https://www.linkedin.com/in/example-profile",
    "role": "Software Engineer",
    "company": "Tech Corp",
    "pain_points": ["scaling challenges", "team coordination"],
    "recent_activity": ["published article on microservices", "spoke at conference"]
  }'
```

### 2. Analyze Profile and Select Anchor
Analyze a profile to select a single anchor point for consistent outreach:

```bash
curl -X POST http://localhost:8000/linkedin/context/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "profile_url": "https://www.linkedin.com/in/example-profile",
    "role": "Product Manager",
    "company": "Startup Inc",
    "recent_activity": ["launched new product", "podcast interview"]
  }'
```

### 3. Interpret Results
The validation result will include:
- `context_depth_score`: A score from 0-4 indicating context richness
- `validation_passed`: Whether the profile has sufficient context
- `generation_mode`: The recommended generation mode (Precision, Safe Personalization, Exploratory)
- `selected_anchor`: The anchor point selected for outreach consistency

## Development

### Running Tests
```bash
pytest tests/linkedin_context_validation/
```

### Running the Service Locally
```bash
uvicorn main:app --reload --port 8000
```

### API Documentation
View the interactive API documentation at `http://localhost:8000/docs` when the service is running.