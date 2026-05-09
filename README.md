# PingGenius Backend

Transform LinkedIn profile information into personalized outreach sequences.

Built with FastAPI for simple, reliable use.

---

## The Story

In October 2025 I started building PingGenius as my first serious AI project.

I wanted to solve a real problem: most LinkedIn outreach tools either scrape data or generate generic messages that get ignored.

After months of work I learned what it takes to make an AI backend reliable:
- avoid incorrect output
- keep responses consistent
- control costs and timeouts
- make messages sound natural

I paused product work for a while to focus on my mental health, but I kept the backend alive because the engineering lessons were valuable.

This is a clean FastAPI backend. It can power a SaaS or be used as a foundation for your own outreach tool.

---

## Core Capabilities

- Smart profile analysis – extracts role, company, industry, pain points, and recent activity
- Personalized sequences – connection notes, DMs, and follow-ups
- Tone control – Friendly, Direct, Authority, Casual
- Message refinement – improve messages while keeping the sequence consistent
- Human-in-the-loop – you copy/paste; no auto-sending
- Pain anchoring – find the main pain point before generating

---

## Technical Features

- FastAPI (async)
- OpenAI Python SDK
- MongoDB
- Authentication and rate limiting
- Swagger/OpenAPI docs
- GDPR-compliant handling
- Timeouts, output sanitization, and idempotency

---

## Quick Start

### Prerequisites
- Python 3.11+
- `uv` package manager (recommended)

### Installation
```bash
git clone https://github.com/hasnainXdev/pinggenius_backend
cd pinggenius_backend

python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

uv add -r requirements.txt
```

## Run locally

```bash
uvicorn main:app --reload
```
Open http://localhost:8000/docs for Swagger UI.

# API Documentation

All v1 endpoints are documented.

Key endpoints:

- POST `/api/v1/profile/analyze` – analyze LinkedIn profile data
- POST `/api/v1/outreach/generate` – generate outreach sequence
- POST `/api/v1/outreach/refine` – refine messages
- GET `/api/v1/outreach/{id}` – retrieve saved sequence

Full docs → `/docs`

# Security & Compliance

- no account risk (copy-paste only)
- GDPR-compliant data handling
- rate limiting and request validation
- timeouts and output checks
- idempotency to avoid duplicate processing

# What I Learned

This project taught me about building an AI backend:

- making outputs predictable
- why many AI tools fail
- why safety layers matter

The main issues were fixed before I considered this ready.

# Development Roadmap
## Must-fix (Completed)

- guard against empty/weak profiles
- deterministic output sanitization
- timeout and runaway protection
- idempotency
- pain anchoring
- sequence cohesion memory
- tone drift protection

## Nice-to-have

- reply-probability scoring
- A/B variants
- LinkedIn policy-safe checker

# Built By
## Muhammad Hasnain
AI Engineer & Full-Stack Developer from Karachi, Pakistan
`hasnainXdev` on GitHub & X

Building useful AI tools for peoples.

For developers: fork it and improve it.