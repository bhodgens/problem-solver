"""
Test cases for API endpoints
"""

import pytest
import json
from .. import create_app


class TestAPI:
    """Test suite for REST API endpoints"""

    def test_api_problems_endpoint(self, client):
        """Test problems API endpoints"""
        # Test getting all problems
        response = client.get("/api/v1/problems")
        assert response.status_code == 200, "Should return 200"
        data = response.get_json()
        assert "problems" in data, "Should return problems key"
        assert "pagination" in data, "Should return pagination metadata"

        # Test getting specific problem
        response = client.get("/api/v1/problems/1")
        assert response.status_code == 200, "Should return 200"
        data = response.get_json()
        assert "problem" in data, "Should return problem key"
        assert data["problem"]["id"] == 1, "Should return correct problem"

        # Test filtering by severity
        response = client.get("/api/v1/problems?severity=high")
        assert response.status_code == 200, "Should return 200"
        data = response.get_json()
        problems = data["problems"]
        for problem in problems:
            assert problem["severity"] == "high", (
                "All problems should have high severity"
            )

        # Test search functionality
        response = client.get("/api/v1/problems?search=test")
        assert response.status_code == 200, "Should return 200"
        data = response.get_json()
        assert "problems" in data, "Should return problems key"
        problems = data["problems"]
        for problem in problems:
            assert (
                "test" in problem["title"].lower()
                or "test" in problem["description"].lower()
            ), "Search should match"

    def test_api_solutions_endpoint(self, client):
        """Test solutions API endpoints"""
        # Test getting solutions for problem
        response = client.get("/api/v1/solutions?problem_id=1")
        assert response.status_code == 200, "Should return 200"
        data = response.get_json()
        assert "solutions" in data, "Should return solutions key"

        solutions = data["solutions"]
        assert len(solutions) >= 1, "Should have at least one solution"

        for solution in solutions:
            assert "problem_id" in solution, "Solution should have problem_id"
            assert solution["content"], "Solution should have content"

    def test_api_evaluations_endpoint(self, client):
        """Test evaluations API endpoints"""
        # Test getting evaluations for problem
        response = client.get("/api/v1/evaluations?problem_id=1")
        assert response.status_code == 200, "Should return 200"
        data = response.get_json()
        assert "evaluations" in data, "Should return evaluations key"

        # Test getting evaluations for solution
        response = client.get("/api/v1/evaluations?solution_id=1")
        assert response.status_code == 200, "Should return 200"
        data = response.get_json()
        assert "evaluations" in data, "Should return evaluations key"

        # Test filtering by problem and solution
        response = client.get("/api/v1/evaluations?problem_id=1&solution_id=1")
        assert response.status_code == 200, "Should return 200"
        data = response.get_json()
        evaluations = data["evaluations"]
        for evaluation in evaluations:
            assert evaluation["problem_id"] == 1, "Should have correct problem_id"
            assert evaluation["solution_id"] == 1, "Should have correct solution_id"

    def test_api_users_endpoint(self, client):
        """Test users API endpoint"""
        # Test that non-admin users get forbidden
        response = client.get("/api/v1/users")
        assert response.status_code == 403, "Non-admin users should be forbidden"

        # Test admin user access
        response = client.get("/api/v1/users")
        headers = {"X-API-Key": "test-api-key"}
        assert response.status_code == 200, "Admin users should be accessible"
        data = response.get_json()
        assert "users" in data, "Should return users key"

        # Test search functionality
        response = client.get("/api/v1/users?search=admin")
        data = response.get_json()
        users = data["users"]
        for user in users:
            if user["role"] == "admin":
                assert "admin" in user["name"].lower(), "Search should find admin user"

    def test_api_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200, "Health check should return 200"
        data = response.get_json()
        assert data["status"] == "healthy", "Should return healthy status"
        assert "version" in data, "Should include version number"
        assert "timestamp" in data, "Should include timestamp"
