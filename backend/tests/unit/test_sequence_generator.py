import pytest
from models.profile import LinkedInProfile
from models.sequence import OutreachSequence, SequenceContext
from services.sequence_generator import SequenceGeneratorService, Tone
from unittest.mock import AsyncMock, MagicMock


class TestSequenceGeneratorService:
    """
    Unit tests for SequenceGeneratorService
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = SequenceGeneratorService()
    
    @pytest.mark.asyncio
    async def test_generate_sequence_with_pain_point(self):
        """Test sequence generation with a specified pain point."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Software Engineer",
            company="Tech Corp",
            industry="Technology",
            pain_point="Scaling team productivity",
            tone="FRIENDLY"
        )
        
        # Mock the agent response
        mock_result = MagicMock()
        mock_result.final_output = "Looking forward to connecting!"
        
        # Since we can't easily mock the Runner.run method, we'll test the other aspects
        # of the sequence generation process
        sequence = await self.service.generate_sequence(profile, Tone.FRIENDLY)
        
        # Verify the sequence was created with the correct properties
        assert sequence.profile_id == ""
        assert sequence.tone == "FRIENDLY"
        assert sequence.connection_note != ""
        assert sequence.dm_1 != ""
        assert sequence.follow_up_1 != ""
        assert sequence.follow_up_2 != ""
    
    @pytest.mark.asyncio
    async def test_generate_sequence_without_pain_point(self):
        """Test sequence generation without a specified pain point."""
        profile = LinkedInProfile(
            url="https://www.linkedin.com/in/test-user",
            role="Sales Manager",
            company="Sales Co",
            industry="Retail",
            pain_point=None,
            tone="DIRECT"
        )
        
        sequence = await self.service.generate_sequence(profile, Tone.DIRECT)
        
        # Verify the sequence was created with the correct properties
        assert sequence.profile_id == ""
        assert sequence.tone == "DIRECT"
        assert sequence.connection_note != ""
        assert sequence.dm_1 != ""
        assert sequence.follow_up_1 != ""
        assert sequence.follow_up_2 != ""
    
    def test_store_and_retrieve_temporary_context(self):
        """Test storing and retrieving temporary sequence context."""
        sequence_id = "test_seq_123"
        context = SequenceContext(
            sequence_id=sequence_id,
            previous_messages=[
                {
                    "position": 1,
                    "role": "Connection Note",
                    "content": "Nice to connect!",
                    "timestamp": 1234567890
                }
            ],
            context_summary="Initial connection made",
            tone_consistency_log=[],
            temporary_storage=True
        )
        
        # Store the context
        self.service._store_temporary_context(sequence_id, context)
        
        # Retrieve the context
        retrieved_context = self.service._retrieve_temporary_context(sequence_id)
        
        # Verify the context was stored and retrieved correctly
        assert retrieved_context is not None
        assert retrieved_context.sequence_id == sequence_id
        assert len(retrieved_context.previous_messages) == 1
        assert retrieved_context.previous_messages[0]["content"] == "Nice to connect!"
        assert retrieved_context.temporary_storage is True
    
    def test_remove_temporary_context(self):
        """Test removing temporary sequence context."""
        sequence_id = "test_seq_456"
        context = SequenceContext(
            sequence_id=sequence_id,
            previous_messages=[],
            context_summary="",
            tone_consistency_log=[],
            temporary_storage=True
        )
        
        # Store and then remove the context
        self.service._store_temporary_context(sequence_id, context)
        self.service._remove_temporary_context(sequence_id)
        
        # Try to retrieve the context (should be None)
        retrieved_context = self.service._retrieve_temporary_context(sequence_id)
        
        assert retrieved_context is None
    
    def test_get_sequence_context_from_temp_storage(self):
        """Test getting sequence context from temporary storage."""
        sequence_id = "test_seq_789"
        context = SequenceContext(
            sequence_id=sequence_id,
            previous_messages=[
                {
                    "position": 1,
                    "role": "Connection Note",
                    "content": "Nice to connect!",
                    "timestamp": 1234567890
                }
            ],
            context_summary="Initial connection made",
            tone_consistency_log=[],
            temporary_storage=True
        )
        
        # Store the context
        self.service._store_temporary_context(sequence_id, context)
        
        # Get the context using the service method
        retrieved_context = self.service.get_sequence_context(sequence_id)
        
        # Verify the context was retrieved correctly
        assert retrieved_context is not None
        assert retrieved_context.sequence_id == sequence_id
        assert len(retrieved_context.previous_messages) == 1
        assert retrieved_context.previous_messages[0]["content"] == "Nice to connect!"
        assert retrieved_context.temporary_storage is True


class TestSequenceCohesion:
    """
    Unit tests specifically for sequence cohesion functionality
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = SequenceGeneratorService()
    
    def test_sequence_context_creation(self):
        """Test creation of sequence context during generation."""
        # Create a temporary sequence context
        sequence_id = "temp_test_seq"
        context = SequenceContext(
            sequence_id=sequence_id,
            previous_messages=[
                {
                    "position": 1,
                    "role": "Connection Note",
                    "content": "Looking forward to connecting!",
                    "timestamp": 1234567890
                },
                {
                    "position": 2,
                    "role": "DM 1",
                    "content": "Hope you're having a great day!",
                    "timestamp": 1234567891
                }
            ],
            context_summary="Initial connection and first message sent",
            tone_consistency_log=[
                {"message_position": 1, "tone_adherence": "high"},
                {"message_position": 2, "tone_adherence": "medium"}
            ],
            temporary_storage=True
        )
        
        # Store the context temporarily
        self.service._store_temporary_context(sequence_id, context)
        
        # Verify it was stored
        retrieved = self.service._retrieve_temporary_context(sequence_id)
        assert retrieved is not None
        assert len(retrieved.previous_messages) == 2
        assert retrieved.context_summary == "Initial connection and first message sent"
    
    def test_sequence_context_persistence_decision(self):
        """Test the decision to persist sequence context."""
        sequence_id = "persist_test_seq"
        context = SequenceContext(
            sequence_id=sequence_id,
            previous_messages=[
                {
                    "position": 1,
                    "role": "Connection Note",
                    "content": "Looking forward to connecting!",
                    "timestamp": 1234567890
                }
            ],
            context_summary="Initial connection made",
            tone_consistency_log=[
                {"message_position": 1, "tone_adherence": "high"}
            ],
            temporary_storage=True
        )
        
        # Store the context temporarily
        self.service._store_temporary_context(sequence_id, context)
        
        # Simulate persistence decision (in a real scenario, this would happen after generation)
        sequence_data = {
            "_id": "mock_object_id",
            "sequence_context": context.dict()
        }
        
        # Persist the context
        result = self.service.persist_sequence_context(sequence_id, sequence_data)
        
        # Verify the persistence operation
        assert result is True
        
        # The context should no longer be in temporary storage
        temp_context = self.service._retrieve_temporary_context(sequence_id)
        assert temp_context is None
    
    def test_sequence_context_access_patterns(self):
        """Test different ways of accessing sequence context."""
        sequence_id = "access_test_seq"
        context = SequenceContext(
            sequence_id=sequence_id,
            previous_messages=[
                {
                    "position": 1,
                    "role": "Connection Note",
                    "content": "Looking forward to connecting!",
                    "timestamp": 1234567890
                }
            ],
            context_summary="Initial connection made",
            tone_consistency_log=[
                {"message_position": 1, "tone_adherence": "high"}
            ],
            temporary_storage=True
        )
        
        # Store in temporary storage
        self.service._store_temporary_context(sequence_id, context)
        
        # Access through the service method
        accessed_context = self.service.get_sequence_context(sequence_id)
        
        # Verify it matches the original
        assert accessed_context is not None
        assert accessed_context.sequence_id == context.sequence_id
        assert len(accessed_context.previous_messages) == len(context.previous_messages)
        assert accessed_context.temporary_storage == context.temporary_storage