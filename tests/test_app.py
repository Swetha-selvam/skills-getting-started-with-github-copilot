import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

    # Check that each activity has the expected structure
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_success(client):
    """Test successful signup for an activity"""
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]
    assert "Chess Club" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_duplicate(client):
    """Test signing up for the same activity twice returns error"""
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")

    # Second signup should fail
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_invalid_activity(client):
    """Test signing up for non-existent activity returns 404"""
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_remove_participant_success(client):
    """Test successful removal of a participant"""
    # First add a participant
    client.post("/activities/Programming%20Class/signup?email=remove@example.com")

    # Now remove them
    response = client.delete("/activities/Programming%20Class/participants?email=remove@example.com")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "remove@example.com" in data["message"]
    assert "Programming Class" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert "remove@example.com" not in activities["Programming Class"]["participants"]


def test_remove_participant_not_found(client):
    """Test removing a participant who is not registered returns 404"""
    response = client.delete("/activities/Chess%20Club/participants?email=notregistered@example.com")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "not registered" in data["detail"].lower()


def test_remove_participant_invalid_activity(client):
    """Test removing from non-existent activity returns 404"""
    response = client.delete("/activities/NonExistent/participants?email=test@example.com")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()