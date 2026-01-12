"""Main application routes"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from ...models.problem import Problem
from ...models.solution import Solution
from ...extensions import db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Main landing page"""
    featured_problems = (
        Problem.query.filter_by(status="open")
        .order_by(Problem.view_count.desc())
        .limit(6)
        .all()
    )
    recent_solutions = (
        Solution.query.join(Problem)
        .filter(Problem.status == "open")
        .order_by(Solution.created_at.desc())
        .limit(4)
        .all()
    )

    # Get recent solutions
    recent_solutions = (
        Solution.query.join(Problem)
        .filter(Problem.status == "open")
        .order_by(Solution.created_at.desc())
        .limit(4)
        .all()
    )

    return render_template(
        "index.html",
        featured_problems=featured_problems,
        recent_solutions=recent_solutions,
    )


@main_bp.route("/about")
def about():
    """About page"""
    return render_template("about.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Redirect to authenticated dashboard"""
    return redirect(url_for("dashboard.index"))


@main_bp.route("/help")
def help():
    """Help page"""
    return render_template("help.html")
