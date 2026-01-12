"""
Problem model for core platform functionality
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Integer, Boolean, JSON
from sqlalchemy.sql import func
from datetime import datetime
from ..extensions import db


class Problem(db.Model):
    """Problem model with status tracking and metadata"""

    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    submitter_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    submitter_pseudonym: Mapped[str] = mapped_column(String(100))
    visibility: Mapped[str] = mapped_column(
        String(50), default="identified"
    )  # anonymous, semi-anonymous, identified
    severity: Mapped[str] = mapped_column(
        String(20), default="medium"
    )  # low, medium, high, critical
    status: Mapped[str] = mapped_column(
        String(50), default="open"
    )  # draft, open, under_review, in_progress, implemented, closed, archived
    affected_departments: Mapped[dict] = mapped_column(
        JSON
    )  # ["Engineering", "HR", etc.]
    tags: Mapped[dict] = mapped_column(JSON)  # [{"name": "IT", "color": "#007bff"}]
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    downvotes: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    submitter: Mapped["User"] = relationship("User", back_populates="problems")
    solutions: Mapped[list["Solution"]] = relationship(
        "Solution", back_populates="problem", cascade="all, delete-orphan"
    )
    evaluations: Mapped[list["ProblemEvaluation"]] = relationship(
        "ProblemEvaluation", back_populates="problem"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="problem", cascade="all, delete-orphan"
    )
    tags_relation: Mapped[list["ProblemTag"]] = relationship(
        "ProblemTag", back_populates="problem"
    )

    def get_vote_score(self):
        """Calculate net vote score"""
        return self.upvotes - self.downvotes

    def get_average_problem_score(self):
        """Calculate average evaluation score from problem evaluations"""
        if not self.evaluations:
            return None

        total = sum(
            eval.severity_rating + eval.impact_rating for eval in self.evaluations
        )
        count = len(self.evaluations)
        return total / count if count > 0 else None

    def get_top_solution(self):
        """Get solution with highest vote score"""
        if not self.solutions:
            return None

        return max(self.solutions, key=lambda s: s.get_vote_score())

    def is_editable_by(self, user):
        """Check if user can edit this problem"""
        return (user and user.id == self.submitter_id) or user.is_admin()

    def is_resolved(self):
        """Check if problem has been implemented"""
        return self.status in ["implemented", "closed"]

    def __repr__(self):
        return f"<Problem {self.title}>"
