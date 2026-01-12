"""
Basic tests for the problem solver application
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from .. import create_app


class TestBasicFunctionality:
    """Test basic application functionality"""

    def test_app_creation(self, app):
        """Test that the application can be created"""
        assert app is not None, "Application should not be None"
        assert app.config["TESTING"], "Should be in testing mode"

    def test_config_override(self, app):
        """Test configuration override"""
        assert app.config["TESTING"], "Should be in testing mode"

    def test_route_access(self, client):
        """Test that routes are accessible"""
        # Test main page
        response = client.get("/")
        assert response.status_code == 200, "Main page should be accessible"
        assert b"Problem Solver" in response.data, "Should contain platform name"

    def test_auth_required_redirect(self, client):
        """Test authentication requirements"""
        # Test accessing protected route without login
        response = client.get("/problems/create")
        assert response.status_code == 302, "Should redirect to login"

        # Test accessing protected route with login
        with client.session_transaction():
            client.post(
                "/auth/login", data={"email": "test@example.com", "password": "test"}
            )
            response = client.get("/problems/create")
            assert response.status_code != 302, "Should not redirect when logged in"

    def test_problem_creation(self, client, sample_user):
        """Test problem creation workflow"""
        with client.session_transaction():
            response = client.post(
                "/problems/create",
                data={
                    "title": "Test Problem",
                    "description": "This is a test problem created during unit testing.",
                    "initial_solutions": ["Solution 1", "Solution 2"],
                    "visibility": "identified",
                    "severity": "medium",
                },
            )

            assert response.status_code == 302, "Should redirect after problem creation"

            # Check that problem was created
            from ..models.problem import Problem

            problem = Problem.query.filter_by(title="Test Problem").first()
            assert problem is not None, "Problem should exist in database"

    def test_api_health(self, client):
        """Test API health endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200, "Health endpoint should return 200"

        data = response.get_json()
        assert data["status"] == "healthy", "Should return healthy status"
        assert "version" in data, "Should include version"
