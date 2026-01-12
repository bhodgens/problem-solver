"""CLI commands for database management and seeding"""

from flask.cli import with_appcontext
from ..extensions import db
from ..models.user import User
from ..models.problem import Problem
from ..models.solution import Solution
from ..models.tag import Tag
from ..utils.anonymizer import Anonymizer


def register_cli(app):
    """Register CLI commands with Flask app"""
    app.cli.add_command(init_db)
    app.cli.add_command(reset_db)
    app.cli.add_command(seed_db)
    app.cli.add_command(create_user)
    app.cli.add_command(list_users)
    app.cli.add_command(process_anonymity_decay)
    app.cli.add_command(send_digest_emails)


@with_appcontext
def init_db():
    """Initialize database with tables"""
    db.create_all()
    print("Database initialized successfully!")


@with_appcontext
def reset_db():
    """Reset database (WARNING: destroys all data)"""
    if input("This will delete all data. Type 'DELETE' to confirm: ") == "DELETE":
        db.drop_all()
        db.create_all()
        print("Database reset successfully!")
    else:
        print("Operation cancelled.")


@with_appcontext
def seed_db():
    """Add sample data for development"""
    from datetime import datetime

    tags_data = [
        {"name": "Engineering", "color": "#007bff"},
        {"name": "Human Resources", "color": "#28a745"},
        {"name": "Finance", "color": "#17a2b8"},
        {"name": "Operations", "color": "#6f42c1"},
        {"name": "Marketing", "color": "#e83e8c"},
    ]

    for tag_data in tags_data:
        tag = Tag(**tag_data)
        db.session.add(tag)

    print(f"Created {len(tags_data)} sample tags")


@with_appcontext
def create_user():
    """Create a new user"""
    email = input("Email: ")
    name = input("Name: ")
    role = input("Role (user/moderator/admin): ")

    if User.query.filter_by(email=email).first():
        print(f"User {email} already exists!")
        return

    user = User(
        email=email, name=name, role=role, pseudonym_seed=email, email_verified=True
    )
    db.session.add(user)
    db.session.commit()

    print(f"User {email} created successfully!")


@with_appcontext
def list_users():
    """List all users"""
    users = User.query.all()
    if not users:
        print("No users found!")
        return

    print("\nUsers:")
    print("-" * 50)
    for user in users:
        status = "Active" if user.is_active else "Inactive"
        print(
            f"ID: {user.id} | Email: {user.email} | Name: {user.name} | Role: {user.role} | Status: {status}"
        )
    print("-" * 50)


@with_appcontext
def process_anonymity_decay():
    """Process anonymity decay for old content"""
    from datetime import datetime, timedelta

    print("Processing anonymity decay...")

    # Get configuration for decay period
    from flask import current_app

    decay_days = current_app.config.get("ANONYMITY_DECAY_DAYS", 30)
    cutoff_date = datetime.utcnow() - timedelta(days=decay_days)

    # Find problems that should have identity revealed
    problems_to_reveal = Problem.query.filter(
        Problem.created_at <= cutoff_date,
        Problem.visibility.in_(["anonymous", "semi-anonymous"]),
    ).all()

    solutions_to_reveal = Solution.query.filter(
        Solution.created_at <= cutoff_date,
        Solution.visibility.in_(["anonymous", "semi-anonymous"]),
    ).all()

    # Process problems
    for problem in problems_to_reveal:
        audit_log = Anonymizer.create_audit_log(
            "anonymity_decay",
            problem.submitter_id,
            {
                "content_type": "problem",
                "content_id": problem.id,
                "original_visibility": problem.visibility,
                "decayed_at": datetime.utcnow().isoformat(),
            },
        )

        # Store audit log (you might want to create an audit_log table)
        print(f"Problem {problem.id} identity revealed due to decay")

    # Process solutions
    for solution in solutions_to_reveal:
        audit_log = Anonymizer.create_audit_log(
            "anonymity_decay",
            solution.submitter_id,
            {
                "content_type": "solution",
                "content_id": solution.id,
                "original_visibility": solution.visibility,
                "decayed_at": datetime.utcnow().isoformat(),
            },
        )

        print(f"Solution {solution.id} identity revealed due to decay")

    total_revealed = len(problems_to_reveal) + len(solutions_to_reveal)
    print(f"Anonymity decay processed: {total_revealed} items revealed")
