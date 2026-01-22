# Implementation Plan: Enhanced Profile Analysis and Outreach Generation

**Branch**: `002-profile-guard` | **Date**: 2026-01-14 | **Spec**: [link to spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-profile-guard/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements enhanced profile analysis and outreach generation with critical safeguards against AI hallucination. The implementation includes validation guards for profile completeness, pain point inference using curated role/industry mappings, sequence cohesion with hybrid storage approach, tone consistency validation with prescriptive rules, and timeout/idempotency protections. The solution builds on the existing FastAPI/MongoDB infrastructure while adding robust validation and quality controls.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Pydantic, Motor (MongoDB), Tenacity (retry logic), [OpenAI Agents Python SDK](https://openai.github.io/openai-agents-python/)
**Storage**: MongoDB (existing database structure)
**Testing**: pytest (with existing test structure)
**Target Platform**: Linux server (containerizable)
**Project Type**: Web API backend
**Performance Goals**:
- API requests complete within 8 seconds (95th percentile)
- Handle 1000+ concurrent users with <200ms response time for validation checks
- Process profile analysis within 5 seconds (95th percentile)
- Support 10k+ daily profile analyses with 99.9% uptime
**Constraints**: <200ms p95 for validation checks, <8s for LLM processing, GDPR compliant data handling
**Scale/Scope**: 10k+ daily profile analyses, 50k+ outreach generations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on the existing constitution file (which is a template), I'll need to apply general software engineering principles:
- Test-first approach: All new functionality must have corresponding tests
- Integration testing: Focus on API contract changes and service interactions
- Observability: Ensure proper logging and error handling
- Simplicity: Start with minimal viable implementation

## Project Structure

### Documentation (this feature)

```text
specs/002-profile-guard/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── api/
│   ├── profile/
│   │   ├── router.py      # Updated with validation logic
│   │   └── validators.py  # New validation module
│   └── outreach/
│       ├── router.py      # Updated with sequence cohesion and tone validation
│       └── validators.py  # New validation module
├── models/
│   ├── profile.py         # Updated with validation methods
│   ├── sequence.py        # Updated with sequence context
│   └── validation.py      # New validation models
├── services/
│   ├── context_extractor.py  # Updated with pain point inference
│   ├── sequence_generator.py # Updated with tone validation and sequence cohesion
│   ├── profile_validation.py # New validation service
│   └── tone_validator.py     # New tone validation service
├── database/
│   └── mongo.py           # Updated with caching for idempotency
├── utils/
│   ├── validation.py      # New validation utilities
│   ├── timeout_manager.py # New timeout utilities
│   └── logging.py         # Updated with enhanced logging
└── tests/
    ├── unit/
    │   ├── test_profile_validation.py
    │   ├── test_tone_validator.py
    │   └── test_context_extractor.py
    ├── integration/
    │   ├── test_profile_api.py
    │   └── test_outreach_api.py
    └── contract/
        └── test_api_contracts.py
```

**Structure Decision**: Single project approach using the existing backend structure. The feature extends existing modules and adds new validation and utility services to implement the required functionality without disrupting the existing architecture.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New validation services | Required for profile completeness and tone consistency | Would compromise quality and safety requirements |
| Enhanced database operations | Needed for idempotency and sequence context | Would risk duplicate charges and inconsistent sequences |
