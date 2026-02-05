# Data Model: LinkedIn Context Validation

## Core Entities

### LinkedInProfile
Represents a LinkedIn profile with required and optional fields for context validation.

**Fields:**
- `id` (str): Unique identifier for the profile
- `role` (str, optional): Professional role/title of the person
- `title` (str, optional): Job title of the person
- `company` (str, optional): Company where the person works
- `industry` (str, optional): Industry of the person's company
- `pain_points` (list[str], optional): Identified pain points from the profile
- `recent_activity` (list[str], optional): Recent activities/posts by the person
- `profile_url` (str): URL to the LinkedIn profile
- `created_at` (datetime): Timestamp when the profile was added
- `updated_at` (datetime): Timestamp when the profile was last updated

**Validation Rules:**
- At least one of `role` OR `title` must be present (identity validation)
- At least one of `company` OR `industry` must be present (affiliation validation)

### ContextValidationResult
Stores the results of context validation for a LinkedIn profile.

**Fields:**
- `profile_id` (str): Reference to the LinkedInProfile
- `context_depth_score` (int): Calculated context depth score (0-4)
- `validation_passed` (bool): Whether the profile passed context validation
- `missing_fields` (list[str]): List of required fields that are missing
- `anchor_point` (str, optional): Selected anchor point for outreach
- `generation_mode` (str): Mode selected based on context depth (Precision, Safe Personalization, Exploratory)
- `validation_timestamp` (datetime): When the validation was performed

**Validation Rules:**
- `context_depth_score` must be between 0 and 4 inclusive
- `generation_mode` must be one of: "Precision", "Safe Personalization", "Exploratory"

### OutreachSequence
A series of messages that maintain context continuity around a single anchor.

**Fields:**
- `id` (str): Unique identifier for the sequence
- `profile_id` (str): Reference to the LinkedInProfile
- `sequence_title` (str): Brief description of the sequence
- `selected_anchor` (str): The anchor point used for the entire sequence
- `messages` (list[OutreachMessage]): Ordered list of messages in the sequence
- `tone_preference` (str): Desired tone for the sequence (Authority, Friendly, Casual)
- `created_at` (datetime): When the sequence was created
- `updated_at` (datetime): When the sequence was last updated

### OutreachMessage
An individual message in an outreach sequence.

**Fields:**
- `id` (str): Unique identifier for the message
- `sequence_id` (str): Reference to the OutreachSequence
- `message_order` (int): Position in the sequence (0 for connection note, 1+ for DMs/follow-ups)
- `content` (str): The actual message content
- `character_count` (int): Number of characters in the message
- `tone_compliant` (bool): Whether the message meets tone requirements
- `contains_prohibited_phrases` (bool): Whether the message contains blacklisted phrases
- `references_anchor` (bool): Whether the message references the selected anchor
- `created_at` (datetime): When the message was created

**Validation Rules:**
- `content` must be ≤ 240 characters
- `message_order` must be ≥ 0

### ContextDepthScoring
Rules for calculating context depth scores.

**Scoring:**
- Role or Title present: +1 point
- Company or Industry present: +1 point
- Pain Points present: +1 point
- Recent Activity present: +1 point
- Maximum possible score: 4 points

**Generation Mode Mapping:**
- Score ≥ 3: Precision Mode
- Score = 2: Safe Personalization Mode
- Score ≤ 1: Exploratory Mode