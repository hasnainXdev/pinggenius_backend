# PingGenius Backend FastAPI

A backend service for PingGenius built with FastAPI.

## Features

- RESTful API endpoints
- Fast performance with FastAPI
- Database integration
- Authentication and authorization
- API documentation with Swagger/OpenAPI

## Getting Started

### Prerequisites

- Python 3.11+
- uv
- virtualenv (recommended)

### Installation

1. Clone the repository

```bash
git clone [https://github.com/hasnainXdev/pinggenius_backend]
```

2. Create and activate virtual environment

```bash
python -m venv venv
```

3. Install dependencies

```bash
uv add -r requirements.txt
```

### Running the Server

```bash
uvicorn main:app --reload
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## PingGenius LinkedIn Outreach Generator

Transform any LinkedIn profile into ultra-personalized, ready-to-send outreach sequences.

### Overview

PingGenius is a blazing-fast AI backend that generates personalized LinkedIn outreach messages from profile URLs. The system extracts context from LinkedIn profiles and creates tailored outreach sequences that sound human and platform-appropriate.

### Features

- **Profile Analysis**: Extract context from LinkedIn profiles including role, company, industry, and recent activity
- **Outreach Generation**: Generate complete outreach sequences with connection note, DMs, and follow-ups
- **Tone Control**: Choose from multiple tones (Friendly, Direct, Authority, Casual) to match your style
- **Message Refinement**: Refine specific messages based on feedback while maintaining sequence consistency
- **Human-in-the-Loop**: Copy-paste approach to maintain account safety (no auto-sending)

### API Endpoints

#### Profile Analysis

- `POST /profile/analyze` - Analyze a LinkedIn profile

#### Outreach Generation

- `POST /outreach/generate` - Generate outreach sequence
- `POST /outreach/refine` - Refine specific messages
- `GET /outreach/{id}` - Retrieve existing sequence

### Security & Compliance

- GDPR compliant data handling
- No account risk (copy-paste only, no auto-sending)
- Rate limiting to prevent API abuse
- Secure API endpoints with proper authentication