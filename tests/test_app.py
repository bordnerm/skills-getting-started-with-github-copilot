import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a test client
client = TestClient(app)

# Original activities data for reset
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball training and games",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Track and Field": {
        "description": "Running, jumping, and throwing events",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["ryan@mergington.edu", "maya@mergington.edu"]
    },
    "Art Studio": {
        "description": "Painting, drawing, and sculpture techniques",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu"]
    },
    "Music Band": {
        "description": "Learn instruments and perform in the school band",
        "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 22,
        "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Thursdays, 3:30 PM - 4:45 PM",
        "max_participants": 16,
        "participants": ["noah@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:45 PM",
        "max_participants": 14,
        "participants": ["jessica@mergington.edu", "ethan@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities dictionary to original state before each test."""
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES)


def test_get_activities():
    """Test retrieving all activities."""
    # Arrange: No special setup needed, activities are reset by fixture

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Check status and response content
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert len(data["Chess Club"]["participants"]) == 2
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange: Choose an activity and a new email
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check success response and that participant was added
    assert response.status_code == 200
    result = response.json()
    assert f"Signed up {email} for {activity_name}" in result["message"]

    # Verify the participant was added
    get_response = client.get("/activities")
    data = get_response.json()
    assert email in data[activity_name]["participants"]


def test_signup_duplicate():
    """Test signup fails when student is already registered."""
    # Arrange: Sign up a student first
    activity_name = "Programming Class"
    email = "dup@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Attempt to sign up the same student again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check for 400 error
    assert response.status_code == 400
    result = response.json()
    assert "Student already signed up" in result["detail"]


def test_signup_invalid_activity():
    """Test signup fails for non-existent activity."""
    # Arrange: Use an invalid activity name
    invalid_activity = "NonExistent Club"
    email = "test@mergington.edu"

    # Act: Make POST request
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")

    # Assert: Check for 404 error
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_unregister_success():
    """Test successful unregistration from an activity."""
    # Arrange: First sign up a student
    activity_name = "Gym Class"
    email = "removeme@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check success response
    assert response.status_code == 200
    result = response.json()
    assert f"Unregistered {email} from {activity_name}" in result["message"]

    # Verify the participant was removed
    get_response = client.get("/activities")
    data = get_response.json()
    assert email not in data[activity_name]["participants"]


def test_unregister_not_signed_up():
    """Test unregistration fails when student is not registered."""
    # Arrange: Try to unregister a student who isn't signed up
    activity_name = "Basketball Team"
    email = "notsignedup@mergington.edu"

    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check for 400 error
    assert response.status_code == 400
    result = response.json()
    assert "Student not signed up" in result["detail"]


def test_unregister_invalid_activity():
    """Test unregistration fails for non-existent activity."""
    # Arrange: Use an invalid activity name
    invalid_activity = "Fake Activity"
    email = "test@mergington.edu"

    # Act: Make DELETE request
    response = client.delete(f"/activities/{invalid_activity}/signup?email={email}")

    # Assert: Check for 404 error
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_root_redirect():
    """Test root endpoint redirects to static index."""
    # Arrange: No special setup

    # Act: Make GET request to root
    response = client.get("/", follow_redirects=False)

    # Assert: Check for redirect response
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"