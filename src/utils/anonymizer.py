"""
Anonymity utilities for quasi-anonymous participation
"""

import hashlib
import random
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from ..extensions import db


class Anonymizer:
    """Handles quasi-anonymous features and pseudonym management"""

    ADJECTIVES = [
        "Creative",
        "Brilliant",
        "Innovative",
        "Strategic",
        "Analytical",
        "Thoughtful",
        "Insightful",
        "Visionary",
        "Methodical",
        "Pragmatic",
        "Collaborative",
        "Resourceful",
        "Adaptable",
        "Proactive",
        "Diligent",
    ]

    NOUNS = [
        "Architect",
        "Engineer",
        "Designer",
        "Strategist",
        "Planner",
        "Thinker",
        "Builder",
        "Creator",
        "Analyst",
        "Facilitator",
        "Coordinator",
        "Specialist",
        "Consultant",
        "Advisor",
        "Expert",
    ]

    @staticmethod
    def generate_pseudonym_seed(email: str) -> str:
        return hashlib.sha256(email.encode()).hexdigest()[:16]

    @staticmethod
    def generate_pseudonym(seed: str) -> str:
        hash_obj = hashlib.md5(seed.encode())
        random.seed(int(hash_obj.hexdigest()[:8], 16))

        adjective = random.choice(Anonymizer.ADJECTIVES)
        noun = random.choice(Anonymizer.NOUNS)
        number = random.randint(100, 999)

        return f"{adjective}{noun}{number}"

    @staticmethod
    def get_user_pseudonym(user) -> str:
        if not user.pseudonym_seed:
            user.pseudonym_seed = Anonymizer.generate_pseudonym_seed(user.email)
            db.session.commit()

        return Anonymizer.generate_pseudonym(user.pseudonym_seed)

    @staticmethod
    def should_reveal_identity(content_item: Any, decay_days: int = 30) -> bool:
        if not hasattr(content_item, "created_at"):
            return False

        if (
            hasattr(content_item, "visibility")
            and content_item.visibility == "identified"
        ):
            return True

        decay_date = content_item.created_at + timedelta(days=decay_days)
        return datetime.utcnow() > decay_date

    @staticmethod
    def get_display_name(user, content_item: Optional[Any] = None, viewer=None) -> str:
        if viewer and viewer.is_admin():
            return user.name or user.email

        if content_item and Anonymizer.should_reveal_identity(content_item):
            return user.name or user.email

        if content_item and hasattr(content_item, "visibility"):
            visibility = content_item.visibility
        else:
            visibility = "identified"

        if visibility == "anonymous":
            return Anonymizer.get_user_pseudonym(user)
        elif visibility == "semi-anonymous":
            if viewer and viewer.is_admin():
                return user.name or user.email
            return Anonymizer.get_user_pseudonym(user)
        else:
            return user.name or user.email

    @staticmethod
    def filter_sensitive_content(
        content: Dict[str, Any], viewer: User
    ) -> Dict[str, Any]:
        filtered = content.copy()

        if not viewer.is_admin():
            admin_fields = ["ip_address", "user_agent", "admin_notes", "internal_flags"]
            for field in admin_fields:
                filtered.pop(field, None)

        return filtered

    @staticmethod
    def apply_anonymity_to_query(query, viewer: User):
        return query

    @staticmethod
    def create_audit_log(
        action: str, user_id: int, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details,
            "category": "anonymity",
        }

    @staticmethod
    def validate_visibility_setting(visibility: str) -> bool:
        valid_settings = ["anonymous", "semi-anonymous", "identified"]
        return visibility in valid_settings

    @staticmethod
    def get_visibility_description(visibility: str) -> str:
        descriptions = {
            "anonymous": "Your identity will be hidden from all users",
            "semi-anonymous": "Your identity will be hidden from regular users but visible to administrators",
            "identified": "Your identity will be visible to all users",
        }
        return descriptions.get(visibility, "Unknown visibility setting")
