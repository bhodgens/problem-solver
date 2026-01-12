"""
Test configuration and fixtures for pytest
"""

import os
import pytest
from datetime import datetime

# Test configuration
TEST_CONFIG = {
    "TESTING": True,
    "WTF_CSRF_ENABLED": False,
    "SECRET_KEY": "test-secret-key",
    "DATABASE_URI": "sqlite:///:memory:",
    "MAIL_DEFAULT_SENDER": "test@example.com",
    "GOOGLE_CLIENT_ID": "test-client-id",
    "GOOGLE_CLIENT_SECRET": "test-client-secret",
    "ANONYMITY_DECAY_DAYS": 1,  # Short for testing
}


@pytest.fixture(scope="session")
def app():
    """Create test application with testing configuration"""
    from .. import create_app

    # Override configuration for testing
    original_config = {}
    for key, value in TEST_CONFIG.items():
        original_config[key] = os.environ.get(key)
        if original_config[key] is None:
            os.environ[key] = value

    app = create_app("testing")

    # Store original config to restore later
    app.original_config = original_config

    with app.app_context():
        db.create_all()
        yield app

    # Restore original config
    for key, value in original_config.items():
        if original_config[key] is not None:
            os.environ[key] = original_config[key]
        elif os.environ.get(key) is not None:
            del os.environ[key]


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    from ..models.user import User
    from ..extensions import db

    user = User(
        email="test@example.com",
        name="Test User",
        role="user",
        pseudonym_seed="test-seed",
        email_verified=True,
        is_active=True,
    )

    db.session.add(user)
    db.session.commit()

    yield user

    with app.app_context():
        db.session.delete(user)


@pytest.fixture
def sample_problem(sample_user):
    """Create a sample problem for testing"""
    from ..models.problem import Problem
    from ..extensions import db

    problem = Problem(
        title="Test Problem",
        description="This is a test problem for unit testing purposes.",
        severity="medium",
        status="open",
        visibility="identified",
        submitter=sample_user,
        affected_departments=["Engineering"],
        view_count=0,
    )

    db.session.add(problem)
    db.session.commit()

    yield problem

    with app.app_context():
        db.session.delete(problem)


@pytest.fixture
def sample_solution(sample_user, sample_problem):
    """Create a sample solution for testing"""
    from ..models.solution import Solution
    from ..extensions import db

    solution = Solution(
        problem_id=sample_problem.id,
        submitter=sample_user,
        content="This is a test solution for unit testing.",
        status="proposed",
        visibility="identified",
        cost_estimate="1000",
        time_estimate="2 weeks",
        required_resources="Development team, budget",
    )

    db.session.add(solution)
    db.session.commit()

    yield solution

    with app.app_context():
        db.session.delete(solution)


@pytest.fixture
def sample_evaluation(sample_user, sample_solution):
    """Create a sample evaluation for testing"""
    from ..models.evaluation import ProblemEvaluation, SolutionEvaluation
    from ..extensions import db

    evaluation = ProblemEvaluation(
        problem_id=sample_problem.id,
        evaluator=sample_user,
        severity_score=4,
        impact_score=4,
        feasibility_score=3,
        creativity_score=5,
        completemess_score=4,
        comments="Test evaluation with comprehensive scoring.",
    )

    db.session.add(evaluation)
    db.session.commit()

    yield evaluation

    with app.app_context():
        db.session.delete(evaluation)


@pytest.fixture
def sample_vote(sample_user, sample_solution):
    """Create a sample vote for testing"""
    from ..models.vote import Vote
    from ..extensions import db

    vote = Vote(
        user_id=sample_user.id,
        solution_id=sample_solution.id,
        score=1,  # Upvote
    )

    db.session.add(vote)
    db.session.commit()

    yield vote

    with app.app_context():
        db.session.delete(vote)


@pytest.fixture
def sample_notification(sample_user):
    """Create a sample notification for testing"""
    from ..models.supporting import Notification
    from ..extensions import db

    notification = Notification(
        user_id=sample_user.id,
        event_type="test_event",
        title="Test Notification",
        message="This is a test notification for unit testing.",
        link="/test-link",
        payload={"test": "data"},
        is_read=False,
    )

    db.session.add(notification)
    db.session.commit()

    yield notification

    with app.app_context():
        db.session.delete(notification)
