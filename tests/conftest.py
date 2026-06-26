"""
Pytest configuration and shared fixtures for the activity management API tests.
Uses AAA (Arrange-Act-Assert) pattern throughout.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


# Initial activities data matching the app's predefined data
INITIAL_ACTIVITIES = {
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
        "description": "Competitive basketball training and tournaments",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu", "james@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Develop tennis skills and compete in matches",
        "schedule": "Tuesdays and Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["sarah@mergington.edu"]
    },
    "Art Studio": {
        "description": "Painting, drawing, and mixed media artistic expression",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "liam@mergington.edu"]
    },
    "Music Band": {
        "description": "Join the school band and perform in concerts",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["grace@mergington.edu", "noah@mergington.edu"]
    },
    "Debate Club": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["lucas@mergington.edu"]
    },
    "Science Club": {
        "description": "Explore scientific concepts through experiments and projects",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 22,
        "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
    }
}


@pytest.fixture(autouse=True)
def reset_activities_before_each_test():
    """
    Reset activities to initial state before each test.
    This fixture is automatically used by all tests (autouse=True).
    Ensures test isolation by providing a fresh, consistent state.
    """
    # Clear the global activities dict
    activities.clear()
    
    # Restore initial state with deep copy of participants lists
    for activity_name, activity_data in INITIAL_ACTIVITIES.items():
        activities[activity_name] = {
            "description": activity_data["description"],
            "schedule": activity_data["schedule"],
            "max_participants": activity_data["max_participants"],
            "participants": activity_data["participants"].copy()  # Copy to avoid reference issues
        }
    
    yield  # Tests run here
    
    # Cleanup after test (optional, next test will reset anyway)


@pytest.fixture
def client():
    """
    Provide a test client for making requests to the FastAPI app.
    Used in the Arrange phase of tests.
    """
    return TestClient(app)


@pytest.fixture
def test_emails():
    """
    Provide test email addresses for students.
    Used in the Arrange phase of tests for signup/unregister operations.
    """
    return {
        "new_student": "new.student@mergington.edu",
        "another_student": "another.student@mergington.edu",
        "third_student": "third.student@mergington.edu",
    }


@pytest.fixture
def small_capacity_activity():
    """
    Provide the name of an activity with small capacity (Tennis Club with max 10).
    Useful for testing full activity scenarios.
    """
    return "Tennis Club"


@pytest.fixture
def large_capacity_activity():
    """
    Provide the name of an activity with large capacity (Gym Class with max 30).
    Useful for testing activities with room for many participants.
    """
    return "Gym Class"
