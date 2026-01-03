---

description: "Task list template for feature implementation"
---

# Tasks: LinkedIn Outreach Generation

**Input**: Design documents from `/specs/001-linkedin-outreach/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan in api/, services/, models/, database/, config/ directories
- [x] T002 Initialize Python project with FastAPI, MongoDB, and required dependencies
- [X] T003 [P] Configure linting and formatting tools (black, flake8, mypy)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [x] T004 Setup MongoDB schema and connection utilities in database/mongo.py
- [x] T005 [P] Configure environment variables and settings management in config/settings.py
- [x] T006 [P] Setup API routing and middleware structure
- [x] T007 Create base models/entities that all stories depend on (LinkedInProfile, OutreachSequence, Message)
- [x] T008 Configure error handling and logging infrastructure
- [x] T009 Setup rate limiting middleware for API endpoints
- [x] T010 Implement retry logic with exponential backoff using tenacity library

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Profile Analysis (Priority: P1) 🎯 MVP

**Goal**: Enable users to analyze LinkedIn profiles and extract context for message generation

**Independent Test**: The system can accept a LinkedIn profile URL as input and return a structured context object containing role, company, industry, and recent activity information.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T011 [P] [US1] Contract test for POST /profile/analyze in tests/contract/test_profile.py
- [ ] T012 [P] [US1] Integration test for profile analysis flow in tests/integration/test_profile.py

### Implementation for User Story 1

- [x] T013 [P] [US1] Create LinkedInProfile model in models/profile.py
- [x] T014 [P] [US1] Create ProfileService in services/profile_scraper.py
- [x] T015 [US1] Implement context extraction logic in services/context_extractor.py
- [x] T016 [US1] Implement POST /profile/analyze endpoint in api/profile/router.py
- [x] T017 [US1] Add validation and error handling for profile analysis
- [x] T018 [US1] Add logging for profile analysis operations
- [x] T019 [US1] Implement error handling for inaccessible LinkedIn profiles (FR-009)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Outreach Sequence Generation (Priority: P1)

**Goal**: Generate complete LinkedIn outreach sequences based on analyzed profile data

**Independent Test**: The system can generate a complete outreach sequence (connection note, DM #1, follow-up #1, follow-up #2) based on profile context data.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T020 [P] [US2] Contract test for POST /outreach/generate in tests/contract/test_outreach.py
- [ ] T021 [P] [US2] Integration test for outreach generation flow in tests/integration/test_outreach.py

### Implementation for User Story 2

- [x] T022 [P] [US2] Create OutreachSequence and Message models in models/sequence.py and models/message.py
- [x] T023 [US2] Implement sequence generation service in services/sequence_generator.py
- [x] T024 [US2] Implement POST /outreach/generate endpoint in api/outreach/router.py
- [x] T025 [US2] Add validation to ensure messages are under 200 characters (SC-003)
- [x] T026 [US2] Add validation to ensure messages are personalized, short, non-salesy, and platform-aware (FR-004)
- [x] T027 [US2] Integrate with profile analysis components (if needed)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Tone Control (Priority: P2)

**Goal**: Allow users to customize the tone of generated outreach messages

**Independent Test**: The system can generate the same outreach sequence in different tones (Friendly, Direct, Authority, Casual) based on the same profile data.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T028 [P] [US3] Contract test for tone selection in tests/contract/test_outreach.py
- [ ] T029 [P] [US3] Integration test for tone-based generation in tests/integration/test_outreach.py

### Implementation for User Story 3

- [x] T030 [P] [US3] Create TonePreference model in models/tone.py
- [x] T031 [US3] Update sequence generator to support tone options (FR-005)
- [x] T032 [US3] Modify POST /outreach/generate endpoint to accept tone parameter (FR-006)
- [x] T033 [US3] Add validation to ensure tone is one of the specified options (FR-005)

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all be independently functional

---

## Phase 6: User Story 4 - Message Refinement (Priority: P3)

**Goal**: Allow users to refine specific messages in their outreach sequences

**Independent Test**: The system can regenerate specific messages in a sequence based on user feedback while maintaining consistency with the overall sequence.

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

- [ ] T034 [P] [US4] Contract test for POST /outreach/refine in tests/contract/test_outreach.py
- [ ] T035 [P] [US4] Integration test for message refinement flow in tests/integration/test_outreach.py

### Implementation for User Story 4

- [x] T036 [P] [US4] Update OutreachSequence model to support refinement states
- [x] T037 [US4] Implement message refinement service in services/sequence_generator.py
- [x] T038 [US4] Implement POST /outreach/refine endpoint in api/outreach/router.py
- [x] T039 [US4] Add validation to maintain message consistency across the sequence (FR-010)
- [x] T040 [US4] Add support for incorporating user feedback in refinement (FR-007)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Additional Requirements Implementation

**Goal**: Implement additional functional requirements from the specification

- [x] T041 Implement GDPR compliance and data minimization practices (FR-011)
- [x] T042 Add clear error messages with actionable alternatives (FR-013)
- [x] T043 Implement copy-paste interface considerations for generated messages (FR-008)
- [x] T044 Add indexes to MongoDB collections as specified in data model

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T045 [P] Documentation updates in docs/
- [X] T046 Code cleanup and refactoring
- [X] T047 Performance optimization across all stories
- [x] T048 [P] Additional unit tests (if requested) in tests/unit/
- [x] T049 Security hardening
- [X] T050 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US2 for sequence generation
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Depends on US2 for sequence generation

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for POST /profile/analyze in tests/contract/test_profile.py"
Task: "Integration test for profile analysis flow in tests/integration/test_profile.py"

# Launch all models for User Story 1 together:
Task: "Create LinkedInProfile model in models/profile.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence