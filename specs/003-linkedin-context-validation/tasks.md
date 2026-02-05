# Tasks: LinkedIn Context Validation

**Feature**: LinkedIn Context Validation
**Branch**: `003-linkedin-context-validation`
**Generated**: 2026-02-04

## Implementation Strategy

**MVP Scope**: Implement User Story 1 (Context Sufficiency Validation) as the minimum viable product, which will provide the core functionality of validating LinkedIn profile context before outreach generation.

**Delivery Approach**: Incremental delivery by user story priority (P1, P2, P3), with each story building upon the previous to form a complete solution. Following test-first development approach with tests written before implementation.

## Phase 1: Setup

- [ ] T001 Create project structure per implementation plan in api/linkedin/
- [ ] T002 Set up environment variables for MongoDB connection in .env
- [ ] T003 Install required dependencies (FastAPI, Pydantic, python-dotenv) in pyproject.toml
- [ ] T004 Initialize MongoDB connection module in database/mongo.py
- [ ] T005 Create base models directory structure in models/
- [ ] T006 Set up pytest configuration and test directory structure in tests/

## Phase 2: Foundational Components

- [ ] T010 [P] Create LinkedInProfile model in models/linkedin_profile.py
- [ ] T011 [P] Create ContextValidationResult model in models/context_validation_result.py
- [ ] T012 [P] Create OutreachSequence model in models/outreach_sequence.py
- [ ] T013 [P] Create OutreachMessage model in models/outreach_message.py
- [ ] T014 [P] Create AnalysisResult model in models/analysis_result.py
- [ ] T015 Create validation engine service in services/validation_engine.py
- [ ] T016 Create context analyzer service in services/context_analyzer.py
- [ ] T017 Create content moderation utilities in utils/content_moderation.py
- [ ] T018 [P] Write unit tests for LinkedInProfile model in tests/models/test_linkedin_profile.py
- [ ] T019 [P] Write unit tests for ContextValidationResult model in tests/models/test_context_validation_result.py
- [ ] T020 [P] Write unit tests for OutreachSequence model in tests/models/test_outreach_sequence.py
- [ ] T021 [P] Write unit tests for OutreachMessage model in tests/models/test_outreach_message.py
- [ ] T022 [P] Write unit tests for AnalysisResult model in tests/models/test_analysis_result.py

## Phase 3: User Story 1 - Context Sufficiency Validation (Priority: P1)

**Story Goal**: Validate that sufficient context exists before generating outreach messages, ensuring high-quality, relevant messages that recipients are more likely to reply to.

**Independent Test**: The system will reject outreach attempts when required context fields are missing and provide a clear indication of what information is needed.

- [ ] T023 [US1] Write unit tests for context validation logic in tests/services/test_validation_engine.py
- [ ] T024 [US1] Write unit tests for context depth scoring algorithm in tests/services/test_validation_engine.py
- [ ] T025 [US1] Write unit tests for required field validation in tests/models/test_linkedin_profile.py
- [ ] T026 [US1] Implement context validation logic in services/validation_engine.py
- [ ] T027 [US1] Implement context depth scoring algorithm in services/validation_engine.py
- [ ] T028 [US1] Implement required field validation (role/title + company/industry) in models/linkedin_profile.py
- [ ] T029 [US1] Write API endpoint tests for context validation in tests/api/test_linkedin_router.py
- [ ] T030 [US1] Create API endpoint for context validation in api/linkedin/router.py
- [ ] T031 [US1] Implement validation response with missing fields in api/linkedin/router.py
- [ ] T032 [US1] Add error handling for invalid input in api/linkedin/router.py

## Phase 4: User Story 2 - Single Anchor Derivation (Priority: P1)

**Story Goal**: Derive a single focal point from available context that remains consistent across the entire outreach sequence, ensuring conversations feel cohesive and relevant.

**Independent Test**: The system consistently selects and references the same anchor point across all messages in a sequence (connection note, DM1, follow-ups).

- [ ] T033 [US2] Write unit tests for anchor selection algorithm in tests/services/test_context_analyzer.py
- [ ] T034 [US2] Write unit tests for anchor priority logic in tests/services/test_context_analyzer.py
- [ ] T035 [US2] Write API endpoint tests for context analysis in tests/api/test_linkedin_router.py
- [ ] T036 [US2] Implement anchor selection algorithm in services/context_analyzer.py
- [ ] T037 [US2] Create anchor priority logic (pain_points > recent_activity > role-based) in services/context_analyzer.py
- [ ] T038 [US2] Add anchor selection to context analysis endpoint in api/linkedin/router.py
- [ ] T039 [US2] Implement anchor consistency validation in services/validation_engine.py
- [ ] T040 [US2] Update OutreachMessage model validation to check anchor references in models/outreach_message.py

## Phase 5: User Story 3 - Low-Context Safeguards (Priority: P2)

**Story Goal**: Handle low-context situations safely by asking diagnostic questions rather than making assumptions, preventing accidental sending of irrelevant or inappropriate messages.

**Independent Test**: When context depth is low (≤1), the system generates exploratory messages that ask questions rather than making assumptions.

- [ ] T041 [US3] Write unit tests for exploratory mode logic in tests/services/test_validation_engine.py
- [ ] T042 [US3] Write unit tests for diagnostic question generation in tests/services/test_context_analyzer.py
- [ ] T043 [US3] Write API endpoint tests for low-context scenarios in tests/api/test_linkedin_router.py
- [ ] T044 [US3] Implement exploratory mode logic in services/validation_engine.py
- [ ] T045 [US3] Create diagnostic question generation in services/context_analyzer.py
- [ ] T046 [US3] Add low-context safeguards to validation engine in services/validation_engine.py
- [ ] T047 [US3] Update context validation endpoint to handle low-context scenarios in api/linkedin/router.py

## Phase 6: User Story 4 - Output Quality Control (Priority: P2)

**Story Goal**: Enforce consistent output quality standards, ensuring all messages meet character limits, tone requirements, and avoid generic phrases that reduce effectiveness.

**Independent Test**: Generated messages conform to specified format requirements (character limits, tone, phrase filtering).

- [ ] T048 [US4] Write unit tests for character limit enforcement in tests/utils/test_content_moderation.py
- [ ] T049 [US4] Write unit tests for prohibited phrases filter in tests/utils/test_content_moderation.py
- [ ] T050 [US4] Write unit tests for tone validation in tests/utils/test_content_moderation.py
- [ ] T051 [US4] Write unit tests for message validation in tests/models/test_outreach_message.py
- [ ] T052 [US4] Implement character limit enforcement (≤240 characters) in utils/content_moderation.py
- [ ] T053 [US4] Create prohibited phrases filter in utils/content_moderation.py
- [ ] T054 [US4] Implement tone validation in utils/content_moderation.py
- [ ] T055 [US4] Add quality control to message generation in services/context_analyzer.py
- [ ] T056 [US4] Update OutreachMessage model validation in models/outreach_message.py

## Phase 7: User Story 5 - Follow-up Consistency (Priority: P3)

**Story Goal**: Maintain context continuity from previous messages in follow-ups, ensuring conversations develop naturally and maintain relevance.

**Independent Test**: Follow-up messages reference the selected anchor and build on previous messages without introducing new topics.

- [ ] T057 [US5] Write unit tests for sequence memory injection in tests/services/test_context_analyzer.py
- [ ] T058 [US5] Write unit tests for follow-up generation logic in tests/services/test_context_analyzer.py
- [ ] T059 [US5] Write unit tests for anchor reference validation in tests/services/test_validation_engine.py
- [ ] T060 [US5] Write unit tests for multiple roles/companies handling in tests/services/test_context_analyzer.py
- [ ] T061 [US5] Implement sequence memory injection in services/context_analyzer.py
- [ ] T062 [US5] Create follow-up generation logic in services/context_analyzer.py
- [ ] T063 [US5] Add anchor reference validation for follow-ups in services/validation_engine.py
- [ ] T064 [US5] Update OutreachSequence model to support follow-up tracking in models/outreach_sequence.py
- [ ] T065 [US5] Implement logic to handle multiple roles/companies (select most relevant/recent) in services/context_analyzer.py

## Phase 8: Internal Scoring and Regeneration

- [ ] T066 Write unit tests for internal scoring mechanism in tests/services/test_validation_engine.py
- [ ] T067 Write unit tests for regeneration logic in tests/services/test_context_analyzer.py
- [ ] T068 Implement internal scoring for messages (context reuse, specificity, human plausibility, question quality) in services/validation_engine.py
- [ ] T069 Implement regeneration with stricter phrasing when internal score falls below threshold in services/context_analyzer.py
- [ ] T070 Update API endpoints to incorporate internal scoring in api/linkedin/router.py

## Phase 9: Integration and Cross-Cutting Concerns

- [ ] T071 Write integration tests for context validation workflow in tests/integration/test_context_validation_flow.py
- [ ] T072 Write integration tests for anchor derivation workflow in tests/integration/test_anchor_derivation_flow.py
- [ ] T073 Write integration tests for complete outreach sequence generation in tests/integration/test_complete_outreach_flow.py
- [ ] T074 Integrate all components and perform end-to-end testing
- [ ] T075 Add comprehensive error handling and logging
- [ ] T076 Implement performance optimizations for context validation
- [ ] T077 Add documentation for the LinkedIn context validation API
- [ ] T078 Perform security review of input validation and sanitization
- [ ] T079 Update README with usage instructions for the new feature

## Dependencies

### User Story Completion Order
1. User Story 1 (Context Sufficiency Validation) - Foundation for all other stories
2. User Story 2 (Single Anchor Derivation) - Builds on context validation
3. User Story 3 (Low-Context Safeguards) - Uses validation results
4. User Story 4 (Output Quality Control) - Applied to all generated content
5. User Story 5 (Follow-up Consistency) - Depends on anchor derivation and sequence tracking

### Component Dependencies
- Models can be developed in parallel (Phase 2)
- Services depend on models (Phase 2 must complete before Phase 3+)
- API endpoints depend on services (Services must complete before endpoints)
- Each user story builds on the previous stories' functionality
- Test files should be created alongside implementation files

## Parallel Execution Examples

### Within User Story 1:
- T023, T024, T025 (unit tests) → T026, T027, T028 (implementation) → T029, T030, T031, T032 (API and endpoint implementation)

### Across User Stories:
- Once US1 is complete, US2, US3, US4 can be worked on in parallel by different developers
- Each story's tests can be written in parallel with its implementation