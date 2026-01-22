# PingGenius Backend FastAPI

Transform any LinkedIn profile into ultra-personalized, ready-to-send outreach sequences.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [API Documentation](#api-documentation)
- [Security & Compliance](#security--compliance)
- [Development Roadmap](#development-roadmap)

---

## Quick Start

### Prerequisites

- Python 3.11+
- `uv` package manager
- virtualenv (recommended)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/hasnainXdev/pinggenius_backend
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   uv add -r requirements.txt
   ```

### Running the Server

```bash
uvicorn main:app --reload
```

Access the API at `http://localhost:8000`

---

## Features

### Core Capabilities

- **Profile Analysis** - Extract context from LinkedIn profiles including role, company, industry, and recent activity
- **Outreach Generation** - Generate complete outreach sequences with connection notes, DMs, and follow-ups
- **Tone Control** - Choose from multiple tones (Friendly, Direct, Authority, Casual) to match your style
- **Message Refinement** - Refine specific messages based on feedback while maintaining sequence consistency
- **Human-in-the-Loop** - Copy-paste approach to maintain account safety (no auto-sending)

### Technical Features

- RESTful API with FastAPI
- Fast performance and async support
- Database integration with MongoDB
- Authentication and authorization
- API documentation with Swagger/OpenAPI
- GDPR compliant data handling
- Rate limiting to prevent API abuse

---

## API Documentation

### Interactive Documentation

Visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

### Profile Analysis Endpoints

| Endpoint           | Method | Description                |
| ------------------ | ------ | -------------------------- |
| `/profile/analyze` | POST   | Analyze a LinkedIn profile |

### Outreach Generation Endpoints

| Endpoint             | Method | Description                |
| -------------------- | ------ | -------------------------- |
| `/outreach/generate` | POST   | Generate outreach sequence |
| `/outreach/refine`   | POST   | Refine specific messages   |
| `/outreach/{id}`     | GET    | Retrieve existing sequence |

---

## Security & Compliance

- ✅ GDPR compliant data handling
- ✅ No account risk (copy-paste only, no auto-sending)
- ✅ Rate limiting to prevent API abuse
- ✅ Secure API endpoints with proper authentication
- ✅ Request validation and sanitization

---

## Development Roadmap

### 🔴 MUST-FIX (before MVP launch)

**Production breakers or silent killers that block launch.**

#### 1. Hard guard: empty / weak profile context

**Problem:** If profile fields are empty, the model fills fluff and generates hallucinated content.

**Solution:** Before running the agent, assert minimum context:

- ❗ `role` (required)
- ❗ `industry` OR `company` (required)

If missing → short-circuit with human fallback copy:

```
"Hey — noticed your profile but didn't have enough context yet"
```

**Why:** Avoids AI hallucination risk.

---

#### 2. Deterministic output safety (very important)

**Problem:** LLMs sometimes return malformed output with quotes, emojis, bullet formatting, or multiple lines.

**Solution:** Before saving, sanitize output:

- Strip newlines
- Force single line
- Remove leading/trailing quotes

**Why:** Prevents broken UI + LinkedIn paste issues. Critical for product trust.

---

#### 3. Timeout / runaway protection

**Problem:** If Gemini hangs → your API hangs.

**Solution:** Add hard timeout per Runner call (8–10s max).

**Why:**

- Prevents queue pileups
- Prevents cold start spikes on Vercel / Fly / Railway
- Ensures predictable API behavior

---

#### 4. Explicit idempotency

**Problem:** If same profile + same tone is requested twice quickly, users burn credits accidentally.

**Solution:**

- Reuse existing sequences for duplicate requests
- Tag generation with `generation_hash`

**Why:** Prevents accidental credit usage and improves efficiency.

---

### 🟡 SHOULD-ADD (high leverage, low effort)

**These multiply quality without redesign.**

#### 5. Pain anchoring helper (cheap W)

**Approach:** Before prompts, derive 1 inferred pain string:

- "Hiring outbound is slow"
- "Manually qualifying leads"
- "Scaling cold outreach"

Pass only ONE pain into context.

**Impact:** LLMs perform far better with focused context: `"Focus on this pain"` vs `"figure out pain from raw data"`.

---

#### 6. Sequence cohesion memory

**Current state:** Each message is generated independently.

**Upgrade:** Inject previous outputs into next prompt:

- DM1 sees connection_note
- Follow-ups see DM1

**Impact:** Increases reply-rate realism. Big outcome, tiny change.

---

#### 7. Tone drift protection

**Problem:** Even with tone enum, models sometimes drift from intended tone.

**Solution:** Add final validation check:

- Friendly → no exclamation spam, max 1 emoji
- Authority → no slang
- Casual → allow light slang

Reject + regenerate once if violated.

**Why:** Protects your brand promise.

---

### 🧠 NICE-LATER (post MVP, don't block launch)

**Nice-to-have features for future versions.**

#### 8. Reply-probability scoring

Use a second cheap model call to score likelihood of reply (1–10 scale). Store internally for future optimization, filters, and upselling.

---

#### 9. A/B sequence variants

Generate 2 versions of sequences, let user pick the better one. This becomes a paid feature later 💸

---

#### 10. LinkedIn policy-safe checker

Auto-detect spammy phrasing, flag risky copy. Not MVP-blocking but important for long-term compliance.
