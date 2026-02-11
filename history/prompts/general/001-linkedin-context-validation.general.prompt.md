---
id: "001"
title: "linkedin-context-validation"
stage: "spec"
date_iso: "2026-02-04"
surface: "agent"
model: "Qwen"
feature: "general"
branch: "003-linkedin-context-validation"
user: "hasnainxdev"
command: "/sp.specify Role You are a senior backend engineer + applied AI architect improving PingGenius using Spec-Driven Development (SDD). Your task is to improve reply-worthiness predictability of LinkedIn outreach by fixing how context is validated, anchored, and reused, without adding scraping, automation, or unsafe behavior. Product Philosophy (Immutable) Context > automation Continuity > clever copy Safety > volume Human plausibility > polish AI must never hallucinate relevance PingGenius is intentionally copy-paste only and human-in-the-loop. Ground Truth (From Real Experiments) The backend was tested against 5 real LinkedIn profiles, rated strictly on: "Would I reply to this?" Observed Quality Ceiling by Context Depth Profile Context LevelAvg Score Strong role + activity + pain signal4.5–5.0 Clear role + company4.0–4.5 Event-based / generic founder3.5–4.0 Generic IT services founder3.1–3.5 Forced vague context~3.0 hard ceiling Key empirical insight AI does not invent relevance. AI amplifies the context it is given. When context is shallow: Language becomes polite Specificity drops Follow-ups decay fastest Replies become optional, not compelling This is a context problem, not a model problem. Core Objective Design a deterministic system that: Predicts outreach quality before generation Degrades safely when context is weak Preserves a single conversational memory thread Prevents false confidence and generic language Makes behavior explainable to developers Context Model (Authoritative) Required Fields (must pass guard) At least ONE from each group: Identity role OR title Affiliation company OR industry If missing → generation must not proceed normally. Optional Fields (ONLY THESE TWO) pain_points recent_activity These fields: Already exist in backend Are not guaranteed Must be handled intentionally ⚠️ No other optional context is assumed. Functional Requirements (Specs) FR-1: Context Sufficiency Gate Before generation: Assert required fields exist Measure context depth score: role/title = +1 company/industry = +1 pain_points present = +1 recent_activity present = +1 Max score: 4 Rules: Score ≥ 3 → Precision Mode Score = 2 → Safe Personalization Mode Score ≤ 1 → Exploratory Mode (FR-4) FR-2: Single Anchor Derivation If pain_points exists: Select exactly ONE pain This becomes the anchor Else if recent_activity exists: Extract ONE observable behavior or theme Convert into inferred anchor Else: Anchor = high-level role-relevant concern (generic but safe) Rules: One anchor per sequence Anchor must appear (explicitly or implicitly) in: connection note DM1 all follow-ups No topic switching. FR-3: Deterministic Output Hygiene Before saving output: One sentence per message No emojis unless tone allows ≤ 240 characters Strip: "intrigued by" "unique challenges" "just checking in" "gentle nudge" Remove quotes and newlines Purpose: Prevent polite-but-forgettable output. FR-4: Exploratory Mode (Low Context Safety) If context depth ≤ 1: Behavior changes: Ask one diagnostic question No assumptions No compliments No invented specificity No mention of "unique challenges" Goal: Invite the prospect to add context, not pretend it exists. This mode caps quality intentionally (~3/5). FR-5: Tone Enforcement Layer After generation, validate tone: Authority No slang No hedging Friendly Max 1 emoji No enthusiasm stacking Casual Conversational allowed No corporate jargon Violation → regenerate once. FR-6: Sequence Memory Injection Follow-ups must receive: Selected anchor connection_note output DM1 output Rules: Follow-ups must: Reference the anchor Add nuance Never reset the conversation No follow-up may introduce a new topic. FR-7: Internal Reply-Worthiness Scoring Internally score each message on: Context reuse Specificity Human plausibility Question quality If average score < threshold: Regenerate with stricter phrasing Never expose score to user Explicit Non-Goals No scraping No auto-sending No lead mixing No personality theater No fake personalization Success Criteria The spec is successful when: Context-rich profiles reliably generate 4.5+ content Vague profiles safely cap at ~3–3.5 without hallucination Follow-ups retain context continuity Developers can predict quality from context depth Users trust outputs enough to copy-paste without fear Guiding Rule (Embed in System Prompt) "If context is weak, ask. If context is strong, focus. Never claim knowledge the profile didn't give you.""
labels:
  - "specification"
  - "linkedin"
  - "context-validation"
links:
  spec: "specs/003-linkedin-context-validation/spec.md"
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "specs/003-linkedin-context-validation/spec.md"
  - "specs/003-linkedin-context-validation/checklists/requirements.md"
tests_yaml: []
prompt_text: "$ARGUMENTS"
response_text: "Created feature specification for LinkedIn context validation with requirements for context sufficiency gates, single anchor derivation, output hygiene, exploratory mode for low-context situations, tone enforcement, sequence memory injection, and internal reply-worthiness scoring."
outcome: "SUCCESS"
evaluation: "Specification successfully created with all required sections, user scenarios, functional requirements, and success criteria. Quality checklist completed and validated."
---

# Feature Specification: LinkedIn Context Validation

**Feature Branch**: `003-linkedin-context-validation`
**Created**: 2026-02-04
**Status**: Draft
**Input**: User description: "Improve reply-worthiness predictability of LinkedIn outreach by fixing how context is validated, anchored, and reused, without adding scraping, automation, or unsafe behavior."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Context Sufficiency Validation (Priority: P1)

As a LinkedIn outreach specialist using PingGenius, I want the system to validate that sufficient context exists before generating outreach messages, so that I can ensure high-quality, relevant messages that recipients are more likely to reply to.

**Why this priority**: This is the foundational requirement that prevents low-quality outreach and ensures the system only operates when there's adequate information to create relevant messages.

**Independent Test**: The system will reject outreach attempts when required context fields are missing and provide a clear indication of what information is needed.

**Acceptance Scenarios**:

1. **Given** a LinkedIn profile with insufficient context (missing required fields), **When** I attempt to generate outreach content, **Then** the system blocks generation and indicates what context is missing
2. **Given** a LinkedIn profile with sufficient context (role/title + company/industry), **When** I attempt to generate outreach content, **Then** the system proceeds with generation
3. **Given** a LinkedIn profile with rich context (role/title + company/industry + pain_points + recent_activity), **When** I attempt to generate outreach content, **Then** the system uses precision mode for generation

---

### User Story 2 - Single Anchor Derivation (Priority: P1)

As a LinkedIn outreach specialist, I want the system to derive a single focal point from available context that remains consistent across the entire outreach sequence, so that conversations feel cohesive and relevant rather than scattered.

**Why this priority**: This ensures conversation continuity and prevents topic switching that reduces reply rates.

**Independent Test**: The system consistently selects and references the same anchor point across all messages in a sequence (connection note, DM1, follow-ups).

**Acceptance Scenarios**:

1. **Given** a LinkedIn profile with pain points identified, **When** generating outreach content, **Then** the system selects exactly one pain point as the anchor and references it in all messages
2. **Given** a LinkedIn profile with recent activity but no pain points, **When** generating outreach content, **Then** the system extracts one observable behavior/theme as the anchor and references it in all messages
3. **Given** a LinkedIn profile with minimal context, **When** generating outreach content, **Then** the system creates a generic but safe anchor based on the role and references it consistently

---

### User Story 3 - Low-Context Safeguards (Priority: P2)

As a LinkedIn outreach specialist, I want the system to handle low-context situations safely by asking diagnostic questions rather than making assumptions, so that I don't accidentally send irrelevant or inappropriate messages.

**Why this priority**: This prevents the system from hallucinating relevance when context is insufficient, maintaining user trust and preventing negative responses.

**Independent Test**: When context depth is low (≤1), the system generates exploratory messages that ask questions rather than making assumptions.

**Acceptance Scenarios**:

1. **Given** a LinkedIn profile with context depth ≤ 1, **When** generating outreach content, **Then** the system enters exploratory mode and asks a diagnostic question
2. **Given** a LinkedIn profile with low context, **When** generating outreach content, **Then** the system avoids compliments, assumptions, and invented specificity

---

### User Story 4 - Output Quality Control (Priority: P2)

As a LinkedIn outreach specialist, I want the system to enforce consistent output quality standards, so that all messages meet character limits, tone requirements, and avoid generic phrases that reduce effectiveness.

**Why this priority**: This ensures consistent, high-quality output that aligns with best practices for LinkedIn outreach.

**Independent Test**: Generated messages conform to specified format requirements (character limits, tone, phrase filtering).

**Acceptance Scenarios**:

1. **Given** any outreach generation request, **When** content is generated, **Then** all messages are ≤240 characters and contain one sentence per message
2. **Given** any outreach generation request, **When** content is generated, **Then** prohibited phrases are removed ("intrigued by", "unique challenges", etc.)
3. **Given** any outreach generation request, **When** content is generated, **Then** tone requirements are enforced (Authority, Friendly, or Casual as specified)

---

### User Story 5 - Follow-up Consistency (Priority: P3)

As a LinkedIn outreach specialist, I want follow-up messages to maintain context continuity from previous messages, so that conversations develop naturally and maintain relevance.

**Why this priority**: This ensures that follow-up sequences build on previous interactions rather than resetting the conversation.

**Independent Test**: Follow-up messages reference the selected anchor and build on previous messages without introducing new topics.

**Acceptance Scenarios**:

1. **Given** a sequence with a selected anchor and previous messages, **When** generating a follow-up, **Then** the follow-up references the anchor and adds nuance
2. **Given** a sequence with previous messages, **When** generating a follow-up, **Then** the follow-up does not introduce a new topic or reset the conversation

---

### Edge Cases

- What happens when a LinkedIn profile has both pain_points and recent_activity? (The system should prioritize pain_points as the anchor)
- How does the system handle profiles with multiple roles or companies? (The system should select the most relevant/recent role and company)
- What if the internal reply-worthiness scoring falls below the threshold? (The system should regenerate with stricter phrasing)
- How does the system handle empty or null values for optional fields? (The system should treat them as absent)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate that at least one identity field (role OR title) exists before allowing outreach generation
- **FR-002**: System MUST validate that at least one affiliation field (company OR industry) exists before allowing outreach generation  
- **FR-003**: System MUST calculate a context depth score: role/title = +1, company/industry = +1, pain_points present = +1, recent_activity present = +1 (Max score: 4)
- **FR-004**: System MUST apply different generation modes based on context depth: Score ≥ 3 → Precision Mode, Score = 2 → Safe Personalization Mode, Score ≤ 1 → Exploratory Mode
- **FR-005**: System MUST select exactly one anchor point when pain_points exist and use it consistently across all messages in the sequence
- **FR-006**: System MUST extract one observable behavior or theme as anchor when recent_activity exists but pain_points don't
- **FR-007**: System MUST create a generic but safe anchor based on role when neither pain_points nor recent_activity exist
- **FR-008**: System MUST ensure all messages in a sequence reference the selected anchor (explicitly or implicitly)
- **FR-009**: System MUST prevent topic switching within a sequence - all messages must relate to the same anchor
- **FR-010**: System MUST enforce output hygiene: one sentence per message, ≤240 characters, no prohibited phrases
- **FR-011**: System MUST strip generic phrases like "intrigued by", "unique challenges", "just checking in", "gentle nudge"
- **FR-012**: System MUST validate tone requirements (Authority, Friendly, Casual) and regenerate if violated
- **FR-013**: System MUST inject sequence memory (selected anchor, previous outputs) into follow-up generation
- **FR-014**: System MUST ensure follow-ups reference the anchor and add nuance without resetting the conversation
- **FR-015**: System MUST internally score messages on context reuse, specificity, human plausibility, and question quality
- **FR-016**: System MUST regenerate with stricter phrasing if internal reply-worthiness score falls below threshold
- **FR-017**: System MUST NOT expose internal scoring to the user
- **FR-018**: System MUST NOT proceed with generation if required fields (identity + affiliation) are missing
- **FR-019**: System MUST NOT allow follow-ups to introduce new topics unrelated to the anchor
- **FR-020**: System MUST NOT hallucinate relevance when context is weak - instead ask diagnostic questions in exploratory mode

### Key Entities

- **LinkedInProfile**: Represents a LinkedIn profile with required fields (role/title, company/industry) and optional fields (pain_points, recent_activity)
- **OutreachSequence**: A series of messages (connection note, DM1, follow-ups) that maintain context continuity around a single anchor
- **AnchorPoint**: A single focal point derived from profile context that guides the entire outreach sequence
- **ContextDepthScore**: A numerical score (0-4) representing the richness of available profile context
- **GenerationMode**: The mode used for content generation (Precision, Safe Personalization, Exploratory) based on context depth

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Context-rich profiles (depth score ≥ 3) reliably generate content rated 4.5+ on "Would I reply to this?" scale
- **SC-002**: Vague profiles (depth score ≤ 1) safely cap at ~3-3.5 rating without hallucination, using exploratory mode appropriately
- **SC-003**: Follow-up messages retain context continuity with 95% of sequences referencing the original anchor point
- **SC-004**: Developers can predict outreach quality from context depth with 90% accuracy based on the scoring system
- **SC-005**: Users trust outputs enough to copy-paste without fear - demonstrated by 80% of users reporting confidence in generated content
- **SC-006**: System prevents generation when required fields are missing in 100% of cases
- **SC-007**: Generated messages comply with format requirements (≤240 characters, one sentence, no prohibited phrases) in 100% of cases
- **SC-008**: Internal reply-worthiness scoring correctly identifies low-quality content for regeneration in 90% of cases