"""
Supporting models for voting, comments, notifications, and tagging
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, Boolean, Text, JSON
from sqlalchemy.sql import func
from datetime import datetime
from ..extensions import db


class Vote(db.Model):
    """Vote model for solution ranking"""

    __tablename__ = "votes"

    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), primary_key=True)
    solution_id: Mapped[int] = mapped_column(
        db.ForeignKey("solutions.id"), primary_key=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 or -1
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="votes")
    solution: Mapped["Solution"] = relationship("Solution", back_populates="votes")

    def __repr__(self):
        return f"<Vote {self.score} by User {self.user_id} for Solution {self.solution_id}>"


class Comment(db.Model):
    """Comment model for solution discussions"""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    solution_id: Mapped[int] = mapped_column(db.ForeignKey("solutions.id"))
    problem_id: Mapped[int] = mapped_column(db.ForeignKey("problems.id"))
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    user_pseudonym: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[int] = mapped_column(db.ForeignKey("comments.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="comments")
    solution: Mapped["Solution"] = relationship("Solution", back_populates="comments")
    problem: Mapped["Problem"] = relationship("Problem", back_populates="comments")
    parent: Mapped["Comment"] = relationship("Comment", remote_side=[id])
    replies: Mapped[list["Comment"]] = relationship("Comment", back_populates="parent")

    def is_editable_by(self, user):
        """Check if user can edit this comment"""
        return (user and user.id == self.user_id) or user.is_admin()

    def __repr__(self):
        return f"<Comment {self.id} by User {self.user_id}>"


class Notification(db.Model):
    """Notification model for user alerts"""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # solution_added, evaluation_received, etc.
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[str] = mapped_column(String(500))
    payload: Mapped[dict] = mapped_column(JSON)  # Additional event data
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.title} for User {self.user_id}>"


class Tag(db.Model):
    """Tag model for categorization"""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    color: Mapped[str] = mapped_column(String(20), default="#6c757d")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    problems_relation: Mapped[list["ProblemTag"]] = relationship(
        "ProblemTag", back_populates="tag"
    )

    def __repr__(self):
        return f"<Tag {self.name}>"


class ProblemTag(db.Model):
    """Association table for problems and tags"""

    __tablename__ = "problem_tags"

    problem_id: Mapped[int] = mapped_column(
        db.ForeignKey("problems.id"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(db.ForeignKey("tags.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    problem: Mapped["Problem"] = relationship("Problem", back_populates="tags_relation")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="problems_relation")

    def __repr__(self):
        return f"<ProblemTag Problem {self.problem_id} - Tag {self.tag_id}>"
