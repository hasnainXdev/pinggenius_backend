# Data Model: Enhanced Profile Analysis and Outreach Generation

## Overview
This document defines the data models for the enhanced profile analysis and outreach generation feature, extending the existing models with validation and context enhancement capabilities. The models are designed to work with the OpenAI Agents Python SDK for content generation.

## Entities

### LinkedIn Profile (Extended)
Represents the input data from a LinkedIn profile, containing role, industry, company, and other contextual information.

**Fields**:
- `id` (str, optional): Unique identifier for the profile in the database
- `url` (str): LinkedIn profile URL
- `role` (str): Professional role/title (REQUIRED for validation)
- `company` (str, optional): Company name (either company or industry required)
- `industry` (str, optional): Industry (either company or industry required)
- `recent_activity` (str, optional): Recent profile activity/signals
- `tone` (str): Requested tone for outreach generation
- `pain_point` (str, optional): Inferred pain point from role/industry
- `context` (dict): Extracted context for outreach generation
- `created_at` (datetime): Timestamp of profile analysis
- `updated_at` (datetime): Timestamp of last update

**Validation Rules**:
- Role field must be present and non-empty
- Either company or industry must be present and non-empty
- URL must be a valid LinkedIn profile URL format
- Tone must be one of the predefined values (Friendly, Direct, Authority, Casual)

### Validation Result
Represents the outcome of profile validation, indicating whether the profile meets minimum requirements.

**Fields**:
- `is_valid` (bool): Whether the profile passed validation
- `errors` (list[str]): List of validation errors if any
- `warnings` (list[str]): List of validation warnings if any
- `required_fields_present` (dict): Map of required fields and their presence status

### Fallback Message
A safe, generic message returned when profile validation fails to prevent AI hallucination.

**Fields**:
- `message` (str): The fallback message content
- `reason` (str): Reason for returning fallback (e.g., "insufficient_context")
- `timestamp` (datetime): When the fallback was generated

### Pain Point
A specific challenge or problem inferred from the profile that the outreach message can address, selected from a curated list of role/industry-specific pain points.

**Fields**:
- `id` (str): Unique identifier for the pain point
- `role` (str): Associated role for this pain point
- `industry` (str, optional): Associated industry for this pain point
- `description` (str): Detailed description of the pain point
- `category` (str): Category of the pain point (e.g., "sales", "marketing", "product")
- `effectiveness_score` (float, optional): Historical effectiveness score

### Sequence Context
Information about previous messages in a sequence that informs the generation of subsequent messages, stored temporarily during generation with option to persist valuable sequences permanently.

**Fields**:
- `sequence_id` (str, optional): ID if sequence is persisted
- `previous_messages` (list[dict]): List of previous messages in the sequence
- `context_summary` (str): Summary of the conversation context
- `tone_consistency_log` (list[dict]): Log of tone validation results
- `temporary_storage` (bool): Whether this context is in temporary storage

### Tone Validator Configuration
Configuration for validating that generated messages adhere to requested tone parameters using prescriptive rules.

**Fields**:
- `tone_type` (str): The tone type (Friendly, Direct, Authority, Casual)
- `emoji_limit` (int): Maximum number of emojis allowed
- `slang_allowed` (bool): Whether slang is allowed
- `formality_level` (int): Formality level (1-5 scale)
- `exclamation_limit` (int): Maximum number of exclamation marks
- `capitalization_rules` (str): Capitalization guidelines

### Outreach Sequence (Extended)
Represents a complete outreach sequence with connection note, DMs, and follow-ups.

**Fields**:
- `id` (str, optional): Unique identifier for the sequence
- `profile_id` (str): Reference to the LinkedIn profile
- `connection_note` (str): Connection request message
- `dm_1` (str): First direct message
- `follow_up_1` (str): First follow-up message
- `follow_up_2` (str): Second follow-up message
- `tone` (str): Tone used for the sequence
- `pain_point_used` (str): Pain point that was incorporated
- `sequence_context` (dict): Context maintained between messages
- `status` (str): Current status (draft, sent, refined, archived)
- `created_at` (datetime): Timestamp of sequence creation
- `updated_at` (datetime): Timestamp of last update

**Validation Rules**:
- All message fields must adhere to the specified tone parameters
- Messages must be properly sanitized (no newlines, quotes removed)
- Tone consistency must be maintained across all messages

## Relationships

### Profile to Sequence
- One LinkedIn Profile can have multiple Outreach Sequences
- Relationship: One-to-Many (profile_id in Outreach Sequence references LinkedIn Profile id)

### Profile to Validation Result
- One LinkedIn Profile has one Validation Result per analysis
- Relationship: One-to-One (embedded in the profile analysis process)

### Sequence to Sequence Context
- One Outreach Sequence has one Sequence Context
- Relationship: One-to-One (sequence_context embedded in Outreach Sequence)

### Pain Point to Profile
- One Pain Point can be associated with many Profiles
- Relationship: One-to-Many (pain_point field in LinkedIn Profile references Pain Point id)

## State Transitions

### Outreach Sequence States
- `draft` → `sent`: When sequence is sent to recipient
- `draft` → `refined`: When sequence is modified based on feedback
- `sent` → `refined`: When sequence is refined after sending
- `draft` | `sent` → `archived`: When sequence is no longer active

### Validation Result States
- `pending` → `valid` | `invalid`: After validation process completes