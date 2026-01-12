"""
Solution model for problem-solving workflow
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Integer, Boolean, JSON, Float
from sqlalchemy.sql import func
from datetime import datetime
from ..extensions import db


class Solution(db.Model):
    """Solution model with voting and evaluation capabilities"""

    __tablename__ = "solutions"

    id: Mapped[int] = mapped_column(primary_key=True)
    problem_id: Mapped[int] = mapped_column(
        db.ForeignKey("problems.id"), nullable=False
    )
    submitter_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    submitter_pseudonym: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    cost_estimate: Mapped[str] = mapped_column(String(100))
    time_estimate: Mapped[str] = mapped_column(String(100))
    required_resources: Mapped[dict] = mapped_column(
        JSON
    )  # ["Budget", "Staff", "Tools"]
    status: Mapped[str] = mapped_column(
        String(50), default="proposed"
    )  # proposed, voting, approved, rejected, implemented
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    downvotes: Mapped[int] = mapped_column(Integer, default=0)
    aggregate_score: Mapped[float] = mapped_column(Float, default=0.0)
    reference_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    problem: Mapped["Problem"] = relationship("Problem", back_populates="solutions")
    submitter: Mapped["User"] = relationship("User", back_populates="solutions")
    evaluations: Mapped[list["SolutionEvaluation"]] = relationship(
        "SolutionEvaluation", back_populates="solution"
    )
    votes: Mapped[list["Vote"]] = relationship(
        "Vote", back_populates="solution", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="solution", cascade="all, delete-orphan"
    )

    def get_vote_score(self):
        """Calculate net vote score"""
        return self.upvotes - self.downvotes

    def get_average_evaluation_score(self):
        """Calculate average evaluation score from all criteria"""
        if not self.evaluations:
            return None

        total_feasibility = sum(eval.feasibility_rating for eval in self.evaluations)
        total_creativity = sum(eval.creativity_rating for eval in self.evaluations)
        total_completeness = sum(eval.completeness_rating for eval in self.evaluations)

        count = len(self.evaluations)
        if count == 0:
            return None

        # Weighted average: Feasibility 40%, Creativity 30%, Completeness 30%
        avg_feasibility = total_feasibility / count * 0.4
        avg_creativity = total_creativity / count * 0.3
        avg_completeness = total_completeness / count * 0.3

        return avg_feasibility + avg_creativity + avg_completeness

    def is_editable_by(self, user):
        """Check if user can edit this solution"""
        return (user and user.id == self.submitter_id) or user.is_admin()

    def is_implemented(self):
        """Check if solution has been implemented"""
        return self.status in ["implemented"]

    def update_aggregate_score(self):
        """Update aggregate score from evaluations"""
        avg_score = self.get_average_evaluation_score()
        self.aggregate_score = avg_score or 0.0

    def __repr__(self):
        return f"<Solution {self.id} for Problem {self.problem_id}>"
