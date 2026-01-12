"""
Test cases for anonymizer utility
"""

import pytest
from datetime import datetime, timedelta
from ..utils.anonymizer import Anonymizer


class TestAnonymizer:
    """Test suite for Anonymizer utility"""

    def test_generate_pseudonym_seed(self):
        """Test pseudonym seed generation"""
        email1 = "test@example.com"
        email2 = "test@example.com"

        seed1 = Anonymizer.generate_pseudonym_seed(email1)
        seed2 = Anonymizer.generate_pseudonym_seed(email2)

        assert seed1 == seed2, "Same email should generate same seed"
        assert len(seed1) == 32, "Seed should be 32 characters"
        assert isinstance(seed1, str), "Seed should be string"

    def test_generate_pseudonym(self):
        """Test pseudonym generation"""
        seed = "test-seed-12345"

        pseudonym1 = Anonymizer.generate_pseudonym(seed)
        pseudonym2 = Anonymizer.generate_pseudonym(seed)

        assert pseudonym1 == pseudonym2, "Same seed should generate same pseudonym"
        assert len(pseudonym1) >= 10, "Pseudonym should be at least 10 characters"
        assert pseudonym1[0].isalpha(), "First character should be alphabetic"
        assert pseudonym1[-1].isdigit(), "Last character should be digit"

    def test_should_reveal_identity(self):
        """Test anonymity decay logic"""
        from datetime import datetime, timedelta

        # Create a mock content item
        class MockContent:
            def __init__(self, days_old):
                self.created_at = datetime.utcnow() - timedelta(days=days_old)
                self.visibility = "anonymous"

                @property
                def is_identified(self):
                    return self.visibility == "identified"

        # Test fresh content (no decay)
        fresh_content = MockContent(days_old=0)
        assert not Anonymizer.should_reveal_identity(fresh_content, 30), (
            "Fresh content should not reveal identity"
        )

        # Test content that should reveal (old)
        old_content = MockContent(days_old=35)  # Older than decay period
        assert Anonymizer.should_reveal_identity(old_content, 30), (
            "Old content should reveal identity"
        )

        # Test identified content
        identified_content = MockContent(days_old=5, visibility="identified")
        assert Anonymizer.should_reveal_identity(identified_content, 30), (
            "Identified content should always reveal identity"
        )

    def test_get_display_name(self):
        """Test display name logic"""
        from ..models.user import User
        from ..utils.anonymizer import Anonymizer

        # Create mock users
        regular_user = User(id=1, name="Regular User")
        admin_user = User(id=2, name="Admin User", role="admin")
        anonymous_user = User(id=3, name="Anonymous User")

        # Create mock content
        class MockContent:
            def __init__(self, visibility="identified", days_old=0):
                self.created_at = datetime.utcnow()
                self.visibility = visibility
                self.submitter = regular_user

        # Test admin user - should always see real names
        admin_name = Anonymizer.get_display_name(
            regular_user, MockContent(visibility="identified"), admin_user
        )
        assert admin_name == "Regular User", (
            "Admin should see real name for identified content"
        )

        # Test regular user with identified content
        regular_name = Anonymizer.get_display_name(
            regular_user, MockContent(visibility="identified"), admin_user
        )
        assert regular_name == "Regular User", (
            "Regular user should see real name for identified content"
        )

        # Test regular user with anonymous content
        regular_anon_name = Anonymizer.get_display_name(
            regular_user, MockContent(visibility="anonymous"), admin_user
        )
        assert "Creative" in regular_anon_name, (
            "Should contain pseudonym for anonymous content"
        )

        # Test anonymous user with any content
        anon_name = Anonymizer.get_display_name(
            anonymous_user, MockContent(visibility="identified"), admin_user
        )
        assert "Creative" in anon_name, (
            "Anonymous user should still see pseudonym for identified content"
        )

    def test_visibility_validation(self):
        """Test visibility setting validation"""
        assert Anonymizer.validate_visibility_setting("identified"), (
            "Valid visibility setting"
        )
        assert Anonymizer.validate_visibility_setting("anonymous"), (
            "Valid visibility setting"
        )
        assert Anonymizer.validate_visibility_setting("semi-anonymous"), (
            "Valid visibility setting"
        )
        assert not Anonymizer.validate_visibility_setting("invalid"), (
            "Invalid visibility setting"
        )

    def test_visibility_description(self):
        """Test visibility description retrieval"""
        desc = Anonymizer.get_visibility_description("identified")
        assert "visible to all users" in desc

        anon_desc = Anonymizer.get_visibility_description("anonymous")
        assert "hidden from all users" in anon_desc

        semi_desc = Anonymizer.get_visibility_description("semi-anonymous")
        assert "hidden from regular users but visible to administrators" in semi_desc

    def test_audit_log_creation(self):
        """Test audit log creation"""
        log = Anonymizer.create_audit_log(
            "test_action", 123, {"test_data": "test_value"}
        )

        assert log["action"] == "test_action", "Action should be preserved"
        assert log["user_id"] == 123, "User ID should be preserved"
        assert log["details"] == {"test_data": "test_value"}, (
            "Details should be preserved"
        )
        assert log["category"] == "anonymity", "Category should be anonymity"
        assert "timestamp" in log, "Timestamp should be included"
