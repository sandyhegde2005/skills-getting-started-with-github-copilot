"""
Tests for the Mergington High School Activities API.
Uses the AAA (Arrange-Act-Assert) pattern.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset participant lists before each test."""
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


@pytest.fixture
def client():
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_all(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "Chess Club" in data

    def test_get_activities_contains_required_fields(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        for activity in data.values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity


class TestSignupForActivity:
    def test_signup_success(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_prevented(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up"


class TestUnregisterFromActivity:
    def test_unregister_success(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_signed_up(self, client):
        # Arrange
        email = "notsignedup@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student is not signed up for this activity"
