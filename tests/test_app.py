import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_all_activities(self, client):
        # ARRANGE - activities are pre-loaded in fixtures
        
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data


    def test_get_activities_returns_correct_structure(self, client):
        # ARRANGE
        expected_keys = {"description", "schedule", "max_participants", "participants"}
        
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        for activity_name, activity_details in data.items():
            assert isinstance(activity_name, str)
            assert set(activity_details.keys()) == expected_keys
            assert isinstance(activity_details["participants"], list)
            assert isinstance(activity_details["max_participants"], int)


    def test_get_activities_includes_participant_data(self, client):
        # ARRANGE
        
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successfully_adds_participant(self, client):
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        initial_participants = len(activities[activity]["participants"])
        
        # ACT
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity}"
        assert email in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_participants + 1


    def test_signup_with_invalid_activity_returns_404(self, client):
        # ARRANGE
        email = "student@mergington.edu"
        invalid_activity = "Nonexistent Club"
        
        # ACT
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


    def test_signup_duplicate_participant_returns_400(self, client):
        # ARRANGE
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        activity = "Chess Club"
        
        # ACT
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
        # Verify no duplicate was added
        assert activities[activity]["participants"].count(email) == 1


    def test_signup_multiple_different_activities(self, client):
        # ARRANGE
        email = "versatile@mergington.edu"
        activities_to_join = ["Chess Club", "Tennis Club"]
        
        # ACT
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            # ASSERT during loop
            assert response.status_code == 200
        
        # ASSERT - verify in both activities
        for activity in activities_to_join:
            assert email in activities[activity]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successfully_removes_participant(self, client):
        # ARRANGE
        email = "michael@mergington.edu"
        activity = "Chess Club"
        initial_count = len(activities[activity]["participants"])
        
        # ACT
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity}"
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count - 1


    def test_unregister_from_invalid_activity_returns_404(self, client):
        # ARRANGE
        email = "student@mergington.edu"
        invalid_activity = "Nonexistent Club"
        
        # ACT
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


    def test_unregister_student_not_in_activity_returns_400(self, client):
        # ARRANGE
        email = "notsigned@mergington.edu"
        activity = "Chess Club"
        
        # ACT
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
        # Verify participants list unchanged
        assert "michael@mergington.edu" in activities[activity]["participants"]


    def test_unregister_then_signup_again(self, client):
        # ARRANGE
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # ACT - Unregister
        response1 = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # ASSERT - Unregister successful
        assert response1.status_code == 200
        assert email not in activities[activity]["participants"]
        
        # ACT - Sign up again
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # ASSERT - Signup successful
        assert response2.status_code == 200
        assert email in activities[activity]["participants"]
