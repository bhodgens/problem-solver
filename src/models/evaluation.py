"""
Evaluation models for multi-criteria assessment system
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, Text, Float
from sqlalchemy.sql import func
from datetime import datetime
from ..extensions import db


class ProblemEvaluation(db.Model):
    """Multi-criteria evaluation for problems"""

    __tablename__ = "problem_evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    problem_id: Mapped[int] = mapped_column(
        db.ForeignKey("problems.id"), nullable=False
    )
    evaluator_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    evaluator_pseudonym: Mapped[str] = mapped_column(String(100))
    severity_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 scale
    impact_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 scale
    comment: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    problem: Mapped["Problem"] = relationship("Problem", back_populates="evaluations")
    evaluator: Mapped["User"] = relationship("User", back_populates="evaluations")

    def get_overall_score(self):
        """Calculate overall score (simple average)"""
        return (self.severity_rating + self.impact_rating) / 2

    def __repr__(self):
        return f"<ProblemEvaluation {self.id} for Problem {self.problem_id}>"


class SolutionEvaluation(db.Model):
    """Multi-criteria evaluation for solutions"""

    __tablename__ = "solution_evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    solution_id: Mapped[int] = mapped_column(
        db.ForeignKey("solutions.id"), nullable=False
    )
    evaluator_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    evaluator_pseudonym: Mapped[str] = mapped_column(String(100))
    feasibility_rating: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 1-5 scale
    creativity_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 scale
    completeness_rating: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 1-5 scale
    comment: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    solution: Mapped["Solution"] = relationship(
        "Solution", back_populates="evaluations"
    )
    evaluator: Mapped["User"] = relationship("User", back_populates="evaluations")

    def get_overall_score(self):
        """Calculate weighted average score"""
        return (
            self.feasibility_rating * 0.4
            + self.creativity_rating * 0.3
            + self.completeness_rating * 0.3
        )

    def __repr__(self):
        return f"<SolutionEvaluation {self.id} for Solution {self.solution_id}>"
