"""REST API blueprint for external integrations"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ...extensions import db
from ...models.user import User
from ...models.problem import Problem
from ...models.solution import Solution
from ...models.evaluation import ProblemEvaluation, SolutionEvaluation
from ...utils.anonymizer import Anonymizer
from sqlalchemy.sql import and_, or_, desc, func

api_bp = Blueprint("api", __name__)


def serialize_user(user, include_email=False):
    """Serialize user data for API response"""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email if include_email else None,
        "role": user.role,
        "pseudonym": user.get_pseudonym(),
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


def serialize_problem(problem, include_submitter=False):
    """Serialize problem data for API response"""
    data = {
        "id": problem.id,
        "title": problem.title,
        "description": problem.description,
        "severity": problem.severity,
        "status": problem.status,
        "visibility": problem.visibility,
        "affected_departments": problem.affected_departments,
        "created_at": problem.created_at.isoformat(),
        "updated_at": problem.updated_at.isoformat() if problem.updated_at else None,
        "view_count": problem.view_count,
        "tags": [],
    }

    if include_submitter and problem.submitter:
        data["submitter"] = serialize_user(problem.submitter)

    # Add tags if available
    if hasattr(problem, "tags") and problem.tags:
        data["tags"] = [
            {"id": tag.id, "name": tag.name, "color": tag.color} for tag in problem.tags
        ]

    return data


def serialize_solution(solution, include_submitter=False):
    """Serialize solution data for API response"""
    data = {
        "id": solution.id,
        "problem_id": solution.problem_id,
        "title": solution.title,
        "content": solution.content,
        "status": solution.status,
        "visibility": solution.visibility,
        "created_at": solution.created_at.isoformat(),
        "cost_estimate": solution.cost_estimate,
        "time_estimate": solution.time_estimate,
        "required_resources": solution.required_resources,
        "vote_score": solution.get_vote_score(),
        "evaluations_count": len(solution.evaluations) if solution.evaluations else 0,
    }

    if include_submitter and solution.submitter:
        data["submitter"] = serialize_user(solution.submitter)

    return data


def serialize_evaluation(evaluation, include_evaluator=False):
    """Serialize evaluation data for API response"""
    data = {
        "id": evaluation.id,
        "problem_id": evaluation.problem_id,
        "solution_id": evaluation.solution_id,
        "severity_score": evaluation.severity_score,
        "impact_score": evaluation.impact_score,
        "feasibility_score": evaluation.feasibility_score,
        "creativity_score": evaluation.creativity_score,
        "completeness_score": evaluation.completeness_score,
        "overall_score": evaluation.get_overall_score(),
        "comments": evaluation.comments,
        "created_at": evaluation.created_at.isoformat(),
    }

    if include_evaluator and evaluation.evaluator:
        data["evaluator"] = serialize_user(evaluation.evaluator)

    return data


@api_bp.route("/problems")
def problems():
    """Get all problems with optional filtering"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    severity = request.args.get("severity")
    status = request.args.get("status")
    search = request.args.get("search")

    query = Problem.query

    if search:
        query = query.filter(
            or_(Problem.title.contains(search), Problem.description.contains(search))
        )

    if severity:
        query = query.filter(Problem.severity == severity)

    if status:
        query = query.filter(Problem.status == status)

    problems = query.order_by(Problem.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        {
            "problems": [
                serialize_problem(problem, include_submitter=True)
                for problem in problems.items
            ],
            "pagination": {
                "page": problems.page,
                "pages": problems.pages,
                "per_page": problems.per_page,
                "total": problems.total,
                "has_prev": problems.has_prev,
                "has_next": problems.has_next,
                "prev_num": problems.prev_num,
                "next_num": problems.next_num,
            },
        }
    )


@api_bp.route("/problems/<int:problem_id>")
def problem_detail(problem_id):
    """Get specific problem details"""
    problem = Problem.query.get_or_404(problem_id)

    # Get solutions and evaluations
    solutions = Solution.query.filter_by(problem_id=problem_id).all()
    evaluations = ProblemEvaluation.query.filter_by(problem_id=problem_id).all()

    return jsonify(
        {
            "problem": serialize_problem(problem, include_submitter=True),
            "solutions": [
                serialize_solution(solution, include_submitter=True)
                for solution in solutions
            ],
            "evaluations": [
                serialize_evaluation(evaluation, include_evaluator=True)
                for evaluation in evaluations
            ],
        }
    )


@api_bp.route("/solutions")
def solutions():
    """Get all solutions with optional filtering"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    problem_id = request.args.get("problem_id", type=int)
    status = request.args.get("status")

    query = Solution.query

    if problem_id:
        query = query.filter(Solution.problem_id == problem_id)

    if status:
        query = query.filter(Solution.status == status)

    solutions = query.order_by(Solution.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        {
            "solutions": [
                serialize_solution(solution, include_submitter=True)
                for solution in solutions.items
            ],
            "pagination": {
                "page": solutions.page,
                "pages": solutions.pages,
                "per_page": solutions.per_page,
                "total": solutions.total,
                "has_prev": solutions.has_prev,
                "has_next": solutions.has_next,
                "prev_num": solutions.prev_num,
                "next_num": solutions.next_num,
            },
        }
    )


@api_bp.route("/solutions/<int:solution_id>")
def solution_detail(solution_id):
    """Get specific solution details"""
    solution = Solution.query.get_or_404(solution_id)

    # Get evaluations
    evaluations = SolutionEvaluation.query.filter_by(solution_id=solution_id).all()

    return jsonify(
        {
            "solution": serialize_solution(solution, include_submitter=True),
            "evaluations": [
                serialize_evaluation(evaluation, include_evaluator=True)
                for evaluation in evaluations
            ],
        }
    )


@api_bp.route("/evaluations")
def evaluations():
    """Get all evaluations with optional filtering"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    problem_id = request.args.get("problem_id", type=int)
    solution_id = request.args.get("solution_id", type=int)

    query = ProblemEvaluation.query.union(SolutionEvaluation.query)

    if problem_id:
        query = query.filter(ProblemEvaluation.problem_id == problem_id)

    if solution_id:
        query = query.filter(SolutionEvaluation.solution_id == solution_id)

    evaluations = query.order_by(ProblemEvaluation.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        {
            "evaluations": [
                serialize_evaluation(evaluation, include_evaluator=True)
                for evaluation in evaluations.items
            ],
            "pagination": {
                "page": evaluations.page,
                "pages": evaluations.pages,
                "per_page": evaluations.per_page,
                "total": evaluations.total,
                "has_prev": evaluations.has_prev,
                "has_next": evaluations.has_next,
                "prev_num": evaluations.prev_num,
                "next_num": evaluations.next_num,
            },
        }
    )


@api_bp.route("/evaluations/<int:evaluation_id>")
def evaluation_detail(evaluation_id):
    """Get specific evaluation details"""
    evaluation = ProblemEvaluation.query.get_or_404(evaluation_id)

    return jsonify(serialize_evaluation(evaluation, include_evaluator=True))


@api_bp.route("/users")
@login_required
def users():
    """Get users (admin only)"""
    if not current_user.is_admin():
        return jsonify({"error": "Admin access required"}), 403

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search")
    role = request.args.get("role")

    query = User.query

    if search:
        query = query.filter(
            or_(User.name.contains(search), User.email.contains(search))
        )

    if role:
        query = query.filter(User.role == role)

    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        {
            "users": [serialize_user(user, include_email=True) for user in users.items],
            "pagination": {
                "page": users.page,
                "pages": users.pages,
                "per_page": users.per_page,
                "total": users.total,
                "has_prev": users.has_prev,
                "has_next": users.has_next,
                "prev_num": users.prev_num,
                "next_num": users.next_num,
            },
        }
    )


@api_bp.route("/stats")
def stats():
    """Get platform statistics"""
    total_problems = Problem.query.count()
    total_solutions = Solution.query.count()
    total_users = User.query.count()
    total_evaluations = (
        ProblemEvaluation.query.count() + SolutionEvaluation.query.count()
    )

    # Get counts by status
    open_problems = Problem.query.filter_by(status="open").count()
    in_progress_problems = Problem.query.filter_by(status="in_progress").count()
    resolved_problems = Problem.query.filter_by(status="resolved").count()

    # Get top users
    top_problem_submitters = (
        db.session.query(
            User.id, User.name, func.count(Problem.id).label("problem_count")
        )
        .join(Problem)
        .group_by(User.id)
        .order_by(func.count(Problem.id).desc())
        .limit(5)
        .all()
    )

    top_solution_submitters = (
        db.session.query(
            User.id, User.name, func.count(Solution.id).label("solution_count")
        )
        .join(Solution)
        .group_by(User.id)
        .order_by(func.count(Solution.id).desc())
        .limit(5)
        .all()
    )

    return jsonify(
        {
            "totals": {
                "problems": total_problems,
                "solutions": total_solutions,
                "users": total_users,
                "evaluations": total_evaluations,
            },
            "problem_status": {
                "open": open_problems,
                "in_progress": in_progress_problems,
                "resolved": resolved_problems,
            },
            "top_contributors": {
                "problems": [
                    {
                        "user": serialize_user(user, include_email=False),
                        "count": problem_count,
                    }
                    for user, problem_count in top_problem_submitters
                ],
                "solutions": [
                    {
                        "user": serialize_user(user, include_email=False),
                        "count": solution_count,
                    }
                    for user, solution_count in top_solution_submitters
                ],
            },
        }
    )


@api_bp.route("/health")
def health():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }
    )


@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Resource not found"}), 404


@api_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return jsonify({"error": "Access forbidden"}), 403


@api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500
