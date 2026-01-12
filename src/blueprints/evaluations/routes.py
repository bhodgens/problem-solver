"""Evaluation routes for multi-criteria assessment"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from ...extensions import db
from ...models.user import User
from ...models.problem import Problem
from ...models.solution import Solution
from ...models.evaluation import ProblemEvaluation, SolutionEvaluation
from sqlalchemy.sql import and_, or_, desc

evaluations_bp = Blueprint("evaluations", __name__)


@evaluations_bp.route("/problem/<int:id>", methods=["GET", "POST"])
@login_required
def evaluate_problem(id):
    """Multi-criteria evaluation for problems"""
    problem = Problem.query.get_or_404(id)

    if request.method == "POST":
        severity_rating = request.form.get("severity_rating", type=int)
        impact_rating = request.form.get("impact_rating", type=int)
        comment = request.form.get("comment", "").strip()

        if not problem or not severity_rating or not impact_rating:
            flash("All fields are required.", "error")
            return redirect(url_for("problems_bp.detail", id=id))

        # Check if user already evaluated this problem
        existing_evaluation = ProblemEvaluation.query.filter_by(
            problem_id=id, evaluator_id=current_user.id
        ).first()

        if existing_evaluation:
            flash("You have already evaluated this problem.", "error")
            return redirect(url_for("problems_bp.detail", id=id))

        evaluation = ProblemEvaluation(
            problem_id=id,
            evaluator_id=current_user.id,
            evaluator_pseudonym=current_user.get_pseudonym(),
            severity_rating=severity_rating,
            impact_rating=impact_rating,
            comment=comment,
        )

        try:
            db.session.add(evaluation)
            db.session.commit()
            flash("Problem evaluation submitted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while evaluating the problem.", "error")

        return redirect(url_for("problems_bp.detail", id=id))


@evaluations_bp.route("/solution/<int:id>", methods=["GET", "POST"])
@login_required
def evaluate_solution(id):
    """Multi-criteria evaluation for solutions"""
    solution = Solution.query.get_or_404(id)

    if request.method == "POST":
        feasibility_rating = request.form.get("feasibility_rating", type=int)
        creativity_rating = request.form.get("creativity_rating", type=int)
        completeness_rating = request.form.get("completeness_rating", type=int)
        comment = request.form.get("comment", "").strip()

        if (
            not solution
            or not feasibility_rating
            or not creativity_rating
            or not completeness_rating
        ):
            flash("All ratings and comment are required.", "error")
            return redirect(url_for("solutions_bp.detail", id=id))

        # Check if user already evaluated this problem
        existing_evaluation = ProblemEvaluation.query.filter_by(
            problem_id=id, evaluator_id=current_user.id
        ).first()

        if existing_evaluation:
            return redirect(url_for("solutions_bp.detail", id=id))

        evaluation = SolutionEvaluation(
            solution_id=id,
            evaluator_id=current_user.id,
            evaluator_pseudonym=current_user.get_pseudonym(),
            feasibility_rating=feasibility_rating,
            creativity_rating=creativity_rating,
            completeness_rating=completeness_rating,
            comment=comment,
        )

        try:
            db.session.add(evaluation)
            db.session.commit()
            flash("Solution evaluation submitted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while evaluating the solution.", "error")

        return redirect(url_for("solutions_bp.detail", id=id))


@evaluations_bp.route("/my-evaluations")
@login_required
def my_evaluations():
    """View user's evaluation history"""
    evaluations = (
        db.session.query(
            ProblemEvaluation.join(Problem), SolutionEvaluation.join(Solution)
        )
        .filter(
            or_(
                ProblemEvaluation.evaluator_id == current_user.id,
                SolutionEvaluation.evaluator_id == current_user.id,
            )
        )
        .order_by(desc("evaluations.created_at"))
        .limit(20)
        .all()
    )

    return render_template("evaluations/my_evaluations.html", evaluations=evaluations)
