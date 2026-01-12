"""Solution management routes"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    jsonify,
    abort,
)
from flask_login import login_required, current_user
from ...extensions import db
from ..models.user import User
from ..models.solution import Solution
from ..models.problem import Problem
from ..models.vote import Vote
from ...utils.notification_manager import NotificationManager
from sqlalchemy.sql import and_, or_, desc

solutions_bp = Blueprint("solutions", __name__)


@solutions_bp.route("/create", methods=["POST"])
@login_required
def create():
    """Create new solution for a problem"""
    problem_id = request.form.get("problem_id", type=int)
    content = request.form.get("content", "").strip()

    if not problem_id or not content:
        flash("Problem ID and solution content are required.", "error")
        return redirect(request.referrer or url_for("problems_bp.list"))

    problem = Problem.query.get_or_404(problem_id)

    solution = Solution(
        problem_id=problem.id,
        submitter_id=current_user.id,
        submitter_pseudonym=current_user.get_pseudonym(),
        content=content,
        status="proposed",
    )

    try:
        db.session.add(solution)
        db.session.commit()

        # Trigger notifications
        NotificationManager.notify_solution_added(solution)

        flash("Solution created successfully!", "success")
        return redirect(url_for("problems_bp.detail", id=problem_id))
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while creating the solution.", "error")
        return redirect(url_for("problems_bp.detail", id=problem_id))


@solutions_bp.route("/<int:id>/vote", methods=["POST"])
@login_required
def vote():
    """Handle voting on solutions"""
    solution_id = request.view_args["id"]
    vote_type = request.form.get("vote_type")

    if solution_id and vote_type in ["upvote", "downvote"]:
        solution = Solution.query.get_or_404(solution_id)

        if not solution:
            return jsonify({"success": False, "message": "Solution not found"}), 404

        # Check if user already voted
        existing_vote = Vote.query.filter_by(
            user_id=current_user.id, solution_id=solution_id
        ).first()

        if existing_vote:
            # Update existing vote
            existing_vote.score = 1 if vote_type == "upvote" else -1
            db.session.commit()
            return jsonify(
                {
                    "success": True,
                    "message": "Vote updated successfully",
                    "vote_score": solution.get_vote_score(),
                }
            )

        # Create new vote
        vote = Vote(
            user_id=current_user.id,
            solution_id=solution_id,
            score=1 if vote_type == "upvote" else -1,
        )
        db.session.add(vote)

        # Update solution vote count
        if vote_type == "upvote":
            solution.upvotes += 1
        else:
            solution.downvotes += 1

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Vote recorded successfully",
                "vote_score": solution.get_vote_score(),
            }
        )


@solutions_bp.route("/<int:id>/detail")
def detail(id):
    """Solution detail view"""
    solution = Solution.query.get_or_404(id)
    problem = solution.problem if solution else None

    if not solution:
        abort(404)

    # Get evaluations
    evaluations = (
        solution.evaluations.order_by(desc("solutions.created_at")).limit(5).all()
    )

    # Get comments
    comments = (
        solution.comments.filter_by(parent_id=None)
        .order_by("solutions.created_at.desc()")
        .limit(10)
        .all()
    )

    return render_template(
        "solutions/detail.html",
        solution=solution,
        problem=problem,
        evaluations=evaluations,
        comments=comments,
    )


@solutions_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    """Edit existing solution"""
    solution = Solution.query.get_or_404(id)

    if not solution or not solution.is_editable_by(current_user):
        abort(403)

    if request.method == "POST":
        content = request.form.get("content", "").strip()

        if not content:
            flash("Content is required.", "error")
            return render_template("solutions/edit.html", solution=solution)

        solution.content = content
        solution.status = request.form.get("status", solution.status)

        try:
            db.session.commit()
            flash("Solution updated successfully!", "success")
            return redirect(url_for("solutions_bp.detail", id=solution.id))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the solution.", "error")

    return render_template("solutions/edit.html", solution=solution)


@solutions_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    """Delete solution"""
    solution = Solution.query.get_or_404(id)

    if not solution or not solution.is_editable_by(current_user):
        abort(403)

    try:
        # Delete solution and related votes/comments
        db.session.delete(solution)
        db.session.commit()
        flash("Solution deleted successfully!", "success")
        return redirect(url_for("problems_bp.detail", id=solution.problem_id))
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the solution.", "error")
