"""
Test cases for database models
"""

import pytest
from .. import create_app


class TestModels:
    """Test database model functionality"""

    def test_user_creation(self, app, sample_user):
        """Test user creation and properties"""
        from ..models.user import User

        # Test that user can be created
        user = User(
            email="test@example.com",
            name="Test User",
            role="user",
            pseudonym_seed="test-seed",
            is_active=True,
            email_verified=True,
        )

        db.session.add(user)
        db.session.commit()

        # Test user properties
        assert user.email == "test@example.com", "Email should be preserved"
        assert user.name == "Test User", "Name should be preserved"
        assert user.role == "user", "Role should be preserved"
        assert user.pseudonym_seed == "test-seed", "Pseudonym seed should be set"
        assert user.is_active is True, "User should be active by default"
        assert user.email_verified is True, "Email should be verified"

        # Test pseudonym generation
        pseudonym = user.get_pseudonym()
        assert pseudonym is not None, "Pseudonym should be generated"
        assert len(pseudonym) >= 10, "Pseudonym should be at least 10 characters"

    def test_problem_creation(self, app, sample_user):
        """Test problem creation and relationships"""
        from ..models.problem import Problem

        with app.app_context():
            problem = Problem(
                title="Test Problem for Models",
                description="This problem tests model relationships.",
                severity="high",
                status="open",
                visibility="identified",
                submitter_id=sample_user.id,
            )

            db.session.add(problem)
            db.session.commit()

            # Test problem properties
            assert problem.title == "Test Problem for Models", (
                "Title should be preserved"
            )
            assert problem.description == "This problem tests model relationships.", (
                "Description should be preserved"
            )
            assert problem.severity == "high", "Severity should be preserved"
            assert problem.status == "open", "Status should be preserved"
            assert problem.visibility == "identified", "Visibility should be preserved"
            assert problem.submitter_id == sample_user.id, "Submitter ID should be set"

            # Test database query
            retrieved = Problem.query.get(problem.id)
            assert retrieved is not None, "Problem should be retrievable"
            assert retrieved.title == problem.title, "Title should match"

    def test_solution_creation(self, app, sample_user, sample_problem):
        """Test solution creation and relationships"""
        from ..models.solution import Solution

        with app.app_context():
            solution = Solution(
                problem_id=sample_problem.id,
                content="Test solution for Models",
                status="proposed",
                visibility="identified",
                submitter_id=sample_user.id,
                cost_estimate="500",
                time_estimate="1 week",
                required_resources="Test resources",
            )

            db.session.add(solution)
            db.session.commit()

            # Test solution properties
            assert solution.problem_id == sample_problem.id, "Problem ID should be set"
            assert solution.content == "Test solution for Models", (
                "Content should be preserved"
            )
            assert solution.status == "proposed", "Status should be preserved"
            assert solution.submitter_id == sample_user.id, "Submitter ID should be set"

            # Test relationship
            retrieved = Solution.query.get(solution.id)
            assert retrieved is not None, "Solution should be retrievable"
            assert retrieved.problem_id == sample_problem.id, (
                "Problem relationship should work"
            )

    def test_evaluation_creation(self, app, sample_user, sample_solution):
        """Test evaluation creation and relationships"""
        from ..models.evaluation import ProblemEvaluation, SolutionEvaluation

        with app.app_context():
            # Test problem evaluation
            problem_eval = ProblemEvaluation(
                problem_id=sample_problem.id,
                evaluator_id=sample_user.id,
                severity_score=5,
                impact_score=4,
                feasibility_score=3,
                creativity_score=4,
                completemess_score=5,
                comments="Test evaluation for problem",
            )

            db.session.add(problem_eval)
            db.session.commit()

            # Test solution evaluation
            solution_eval = SolutionEvaluation(
                solution_id=sample_solution.id,
                evaluator_id=sample_user.id,
                severity_score=4,
                impact_score=4,
                feasibility_score=3,
                creativity_score=5,
                completemess_score=4,
                comments="Test evaluation for solution",
            )

            db.session.add(solution_eval)
            db.session.commit()

            # Test evaluation relationships
            retrieved = ProblemEvaluation.query.get(problem_eval.id)
            assert retrieved is not None, "Problem evaluation should be retrievable"
            assert retrieved.evaluator_id == sample_user.id, "Evaluator ID should match"
            assert retrieved.problem_id == sample_problem.id, "Problem ID should match"

    def test_vote_creation(self, app, sample_user, sample_solution):
        """Test vote creation and relationships"""
        from ..models.vote import Vote

        with app.app_context():
            vote = Vote(user_id=sample_user.id, solution_id=sample_solution.id, score=1)

            db.session.add(vote)
            db.session.commit()

            # Test vote properties and relationships
            retrieved = Vote.query.get(vote.id)
            assert retrieved is not None, "Vote should be retrievable"
            assert retrieved.user_id == sample_user.id, "User ID should match"
            assert retrieved.solution_id == sample_solution.id, (
                "Solution ID should match"
            )
            assert retrieved.score == 1, "Vote score should match"

    def test_notification_creation(self, app, sample_user):
        """Test notification creation and relationships"""
        from ..models.supporting import Notification

        with app.app_context():
            notification = Notification(
                user_id=sample_user.id,
                event_type="test_event",
                title="Test Notification",
                message="Test notification for unit testing",
                link="/test-link",
                payload={"test": "data"},
                is_read=False,
            )

            db.session.add(notification)
            db.session.commit()

            # Test notification properties
            retrieved = Notification.query.get(notification.id)
            assert retrieved is not None, "Notification should be retrievable"
            assert retrieved.user_id == sample_user.id, "User ID should match"
            assert retrieved.title == "Test Notification", "Title should match"
            assert not retrieved.is_read, "Notification should be unread by default"
