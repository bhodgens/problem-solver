"""Problem management routes"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    abort,
)
from flask_login import login_required, current_user as current_user_func
from flask_sqlalchemy.pagination import Pagination
from ...extensions import db
from ...models.user import User
from ...models.problem import Problem
from ...models.solution import Solution
from ...models.tag import Tag, ProblemTag
from ...utils.anonymizer import Anonymizer
from ...utils.notification_manager import NotificationManager
from sqlalchemy.sql import and_, or_, desc

problems_bp = Blueprint("problems", __name__)


@problems_bp.route("/")
def list():
    """Browse problems with search and filters"""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")
    severity = request.args.get("severity", "")
    status_filter = request.args.get("status", "")
    tag_filter = request.args.get("tag", "")

    query = Problem.query

    if search:
        query = query.filter(
            or_(Problem.title.contains(search), Problem.description.contains(search))
        )

    if severity:
        query = query.filter(Problem.severity == severity)

    if status_filter:
        query = query.filter(Problem.status == status_filter)

    if tag_filter:
        # TODO: Implement tag filtering when tag model is created
        # query = (
        #     query.join(Problem.tags_relation).join(Tag).filter(Tag.name == tag_filter)
        # )
        pass

    problems = query.order_by(Problem.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template(
        "problems/list.html",
        problems=problems,
        search=search,
        severity=severity,
        status_filter=status_filter,
        tag_filter=tag_filter,
        current_page=page,
        current_user=current_user,
        get_display_name=Anonymizer.get_display_name,
    )


@problems_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create new problem with solutions"""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        initial_solutions = request.form.getlist("solutions")
        # TODO: Implement tag handling when tag model is created
        # problem_tags = request.form.getlist("tags")
        # for tag_name in problem_tags:
        #     tag = Tag.query.filter_by(name=tag_name.strip()).first()
        #     if not tag:
        #         tag = Tag(name=tag_name.strip(), description=f"Tag for {tag_name}")
        #         db.session.add(tag)
        #         db.session.flush()
        #
        #     problem_tag = ProblemTag(problem_id=problem.id, tag_id=tag.id)
        #         db.session.add(problem_tag)

        if not title or not description:
            flash("Title and description are required.", "error")
            return render_template(
                "problems/create.html",
                title=title,
                description=description,
                initial_solutions=initial_solutions,
                problem_tags=[],
                visibility="identified",
                severity="medium",
            )

        problem = Problem(
            title=title,
            description=description,
            submitter_id=current_user.id,
            submitter_pseudonym=current_user.get_pseudonym(),
            visibility=visibility,
            severity=severity,
            affected_departments=request.form.getlist("departments"),
            status="open",
        )

        try:
            db.session.add(problem)
            db.session.commit()

            # Trigger notifications
            NotificationManager.notify_problem_created(problem)

            flash("Problem created successfully!", "success")
            return redirect(url_for("problems_bp.detail", id=problem.id))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while creating problem.", "error")
            current_app.logger.error(f"Problem creation error: {str(e)}")
            return render_template(
                "problems/create.html",
                title=title,
                description=description,
                initial_solutions=initial_solutions,
                problem_tags=[],
                visibility="identified",
                severity="medium",
            )

    return render_template("problems/create.html")

    return render_template("problems/create.html")


@problems_bp.route("/<int:id>")
def detail(id):
    """Problem detail view with solutions and evaluations"""
    problem = Problem.query.get_or_404(id)

    if request.method == "POST":
        if not problem.is_editable_by(current_user):
            abort(403)

        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")
        visibility = request.form.get("visibility")
        severity = request.form.get("severity")

        if title:
            problem.title = title
        if description:
            problem.description = description
        if status:
            problem.status = status
        if visibility:
            problem.visibility = visibility
        if severity:
            problem.severity = severity

        try:
            db.session.commit()
            flash("Problem updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the problem.", "error")

    solutions = (
        Solution.query.filter_by(problem_id=id)
        .order_by(Solution.created_at.desc())
        .all()
    )

    return render_template(
        "problems/detail.html",
        problem=problem,
        solutions=solutions,
        is_editable=problem.is_editable_by(current_user),
        current_user=current_user,
        get_display_name=Anonymizer.get_display_name,
    )


@problems_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    """Edit existing problem"""
    problem = Problem.query.get_or_404(id)

    if not problem.is_editable_by(current_user):
        abort(403)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        visibility = request.form.get("visibility", problem.visibility)
        severity = request.form.get("severity", problem.severity)

        if title:
            problem.title = title
        if description:
            problem.description = description
        if visibility:
            problem.visibility = visibility
        if severity:
            problem.severity = severity

        try:
            db.session.commit()
            flash("Problem updated successfully!", "success")
            return redirect(url_for("problems_bp.detail", id=problem.id))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the problem.", "error")

    return render_template("problems/edit.html", problem=problem, is_editable=True)


@problems_bp.route("/search")
def search():
    """Search results page"""
    query = request.args.get("q", "")

    problems = (
        Problem.query.filter(
            or_(Problem.title.contains(query), Problem.description.contains(query))
        )
        .order_by(Problem.created_at.desc())
        .limit(50)
        .all()
    )

    return render_template(
        "problems/search_results.html", problems=problems, query=query
    )
