# PingGenius Backend

**Transform any LinkedIn profile into ultra-personalized, ready-to-send outreach sequences.**

Built with production-grade safety and reliability in mind.

---

## 📖 The Story

In October 2025 I started building PingGenius as my first serious AI agent project.

I wanted to solve a real problem: most LinkedIn outreach tools either scrape (risky) or generate generic messages that get ignored.

After months of iteration I learned the hard way what it actually takes to make an LLM-powered system reliable in production:
- Guarding against hallucinations
- Enforcing deterministic output
- Protecting against runaway costs and timeouts
- Keeping sequences human-like and safe

I ghosted the product side for a while to focus on my mental health and other work… but I kept the backend alive because the engineering lessons were too valuable.

Today this is a **clean, battle-tested FastAPI + LangGraph backend** that I’m proud of.  
It’s ready to power a full SaaS or be used as a foundation for your own outreach tool.

Alhumdulillah for the grind.

---

## ✨ Core Capabilities

- **Smart Profile Analysis** – Extracts role, company, industry, pain points and recent activity
- **Ultra-Personalized Sequences** – Generates connection notes, DMs and follow-ups in your chosen tone
- **Tone Control** – Friendly, Direct, Authority, or Casual
- **Message Refinement** – Improve any message while keeping the whole sequence consistent
- **100% Human-in-the-Loop** – You copy-paste. No auto-sending → zero account risk
- **Pain Anchoring** – Automatically finds the one real pain point before generating

---

## 🛠 Technical Features

- FastAPI (async + production ready)
- LangGraph for reliable agent state management
- MongoDB for persistence
- Full authentication & rate limiting
- Swagger/OpenAPI docs
- GDPR compliant
- Hard timeouts, output sanitization, idempotency, and hallucination guards

---

## 🚀 Quick Start

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
Open http://localhost:8000/docs for interactive Swagger UI.

# 📡 API Documentation

All v1 endpoints are clean and documented.

**Key endpoints:**

- POST `/api/v1/profile/analyze` – Analyze LinkedIn profile data
- POST `/api/v1/outreach/generate` – Generate full outreach sequence
- POST `/api/v1/outreach/refine` – Refine specific messages
- GET `/api/v1/outreach/{id}` – Retrieve saved sequence

Full interactive docs → `/docs`
Note: The API accepts profile data directly (no scraping). Safe and compliant.

# 🔐 Security & Compliance

- ✅ No account risk (copy-paste only)
- ✅ GDPR compliant data handling
- ✅ Rate limiting + request validation
- ✅ Hard timeouts and output sanitization
- ✅ Idempotency to prevent duplicate charges

# 🧠 What I Learned (Most Valuable Part)
This project taught me more about building reliable AI agents than any course:

- How to make LLMs actually predictable
- Why most AI tools fail in production
- The importance of safety layers before fancy features

All the “MUST-FIX” items you see below were completed before I considered this production-ready.

# 🛣 Development Roadmap
## 🔴 MUST-FIX (All Completed ✅)

- Hard guard against empty/weak profiles
- Deterministic output sanitization
- Timeout & runaway protection
- Explicit idempotency
- Pain anchoring
- Sequence cohesion memory
- Tone drift protection

## 🟡 Nice-to-have (Post-MVP)

- Reply-probability scoring
- A/B sequence variants
- LinkedIn policy-safe checker

# 👤 Built By
## Muhammad Hasnain
AI Engineer & Full-Stack Developer from Karachi, Pakistan
`hasnainXdev` on GitHub & X

Building halal, useful AI tools for Pakistani businesses and developers.

**For developers**: Fork it, improve it, build on it.
**For businesses**: Want personalized LinkedIn outreach that actually works? DM me I can help you run this backend or build the full product.
Currently open to remote AI/FastAPI roles and local client projects.
