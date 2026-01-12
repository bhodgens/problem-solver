"""Dashboard routes"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy.sql import and_, or_, desc, func
from ...extensions import db
from ...models.user import User
from ...models.problem import Problem
from ...models.solution import Solution
from ..models.notification import Notification
from sqlalchemy.orm import joinedload

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Personalized dashboard with widgets"""
    user = current_user

    # Get user's problems
    my_problems = (
        Problem.query.filter_by(submitter_id=user.id)
        .order_by(Problem.created_at.desc())
        .limit(5)
        .all()
    )

    # Get problems to evaluate (exclude user's own)
    problems_to_evaluate = (
        Problem.query.filter(Problem.status == "open", Problem.submitter_id != user.id)
        .order_by(Problem.created_at.desc())
        .limit(5)
        .all()
    )

    # Get user's solutions that need evaluation
    solutions_to_evaluate = (
        db.session.query(Solution)
        .join(Problem)
        .filter(
            Solution.submitter_id == user.id,
            Solution.status.in_(["proposed", "voting"]),
        )
        .options(joinedload(Problem.evaluations))
        .filter(SolutionEvaluation.evaluator_id != user.id)
        .limit(5)
        .all()
    )

    # Get notifications
    notifications = (
        Notification.query.filter_by(user_id=user.id, is_read=False).limit(10).all()
    )

    # Calculate statistics
    total_problems = Problem.query.filter_by(submitter_id=user.id).count()
    open_problems = Problem.query.filter_by(submitter_id=user.id, status="open").count()
    resolved_problems = Problem.query.filter_by(
        submitter_id=user.id, status="implemented"
    ).count()
    high_severity_problems = Problem.query.filter_by(
        submitter_id=user.id, severity="critical"
    ).count()

    return render_template(
        "dashboard/index.html",
        my_problems=my_problems,
        problems_to_evaluate=problems_to_evaluate,
        solutions_to_evaluate=solutions_to_evaluate,
        notifications=notifications,
        stats={
            "total_problems": total_problems,
            "open_problems": open_problems,
            "resolved_problems": resolved_problems,
            "high_severity_problems": high_severity_problems,
        },
    )
