"""
User model with OAuth integration and role management
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Boolean
from datetime import datetime
from ..extensions import db
from ..utils.anonymizer import Anonymizer


class User(db.Model):
    """User model for authentication and role management"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[str] = mapped_column(String(500))
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    pseudonym_seed: Mapped[str] = mapped_column(String(100))
    visibility_preference: Mapped[str] = mapped_column(String(20), default="identified")
    email_notifications: Mapped[str] = mapped_column(String(20), default="daily")
    digest_frequency: Mapped[str] = mapped_column(String(20), default="morning")
    notification_types: Mapped[str] = mapped_column(
        String(200), default="problems,solutions,evaluations"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[datetime] = mapped_column(DateTime)

    # Relationships
    problems: Mapped[list["Problem"]] = relationship(
        "Problem", back_populates="submitter", cascade="all, delete-orphan"
    )
    solutions: Mapped[list["Solution"]] = relationship(
        "Solution", back_populates="submitter", cascade="all, delete-orphan"
    )
    evaluations: Mapped[list["Evaluation"]] = relationship(
        "Evaluation", back_populates="evaluator"
    )
    votes: Mapped[list["Vote"]] = relationship("Vote", back_populates="user")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user"
    )

    def get_unread_notifications_count(self) -> int:
        """Get count of unread notifications for this user"""
        return sum(1 for notif in self.notifications if not notif.is_read)

    def get_pseudonym(self):
        return Anonymizer.get_user_pseudonym(self)

    def is_admin(self):
        """Check if user has admin role"""
        return self.role in ["admin", "moderator"]

    def get_display_name(self, content_item=None, viewer=None):
        from flask import session

        if not viewer and hasattr(session, "get"):
            viewer = session.get("current_user")

        return Anonymizer.get_display_name(self, content_item, viewer)

    def __repr__(self):
        return f"<User {self.email}>"
