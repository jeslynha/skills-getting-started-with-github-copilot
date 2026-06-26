"""
Integration tests for the High School Activity Management System API.
All tests follow the AAA (Arrange-Act-Assert) pattern for clarity.

Arrange: Set up test data, fixtures, and initial state
Act: Execute the endpoint or operation being tested
Assert: Verify the result matches expectations
"""

import pytest


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        Test successful retrieval of all activities.
        
        Arrange: Get test client
        Act: GET /activities
        Assert: Returns 200 with all 9 activities
        """
        # Arrange
        expected_activity_count = 9
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Art Studio", "Music Band", "Debate Club", "Science Club"
        ]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        for activity_name in expected_activities:
            assert activity_name in activities
    
    def test_get_activities_contains_required_fields(self, client):
        """
        Test that activities response contains required fields.
        
        Arrange: Get test client
        Act: GET /activities
        Assert: Each activity has description, schedule, max_participants, participants
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == required_fields, \
                f"Activity '{activity_name}' missing required fields"
    
    def test_get_activities_shows_correct_participant_count(self, client):
        """
        Test that activities show correct number of participants.
        
        Arrange: Get test client
        Act: GET /activities
        Assert: Participant count matches expected values
        """
        # Arrange - Expected participant counts based on initial data
        expected_counts = {
            "Chess Club": 2,
            "Programming Class": 2,
            "Gym Class": 2,
            "Basketball Team": 2,
            "Tennis Club": 1,
            "Art Studio": 2,
            "Music Band": 2,
            "Debate Club": 1,
            "Science Club": 2
        }
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, expected_count in expected_counts.items():
            assert len(activities[activity_name]["participants"]) == expected_count, \
                f"Activity '{activity_name}' has wrong participant count"
    
    def test_get_activities_has_correct_capacities(self, client):
        """
        Test that activities have correct max_participants capacity.
        
        Arrange: Get test client
        Act: GET /activities
        Assert: Capacities match expected values
        """
        # Arrange
        expected_capacities = {
            "Chess Club": 12,
            "Programming Class": 20,
            "Gym Class": 30,
            "Basketball Team": 15,
            "Tennis Club": 10,
            "Art Studio": 18,
            "Music Band": 25,
            "Debate Club": 16,
            "Science Club": 22
        }
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, expected_capacity in expected_capacities.items():
            assert activities[activity_name]["max_participants"] == expected_capacity, \
                f"Activity '{activity_name}' has wrong capacity"
    
    def test_get_activities_response_is_json_dict(self, client):
        """
        Test that response is a valid JSON dictionary.
        
        Arrange: Get test client
        Act: GET /activities
        Assert: Response is a dictionary and can be parsed as JSON
        """
        # Arrange
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success_for_activity(self, client, test_emails):
        """
        Test successful signup for an activity.
        
        Arrange: Select activity and test email
        Act: POST /activities/Chess Club/signup with email
        Assert: Returns 200 and participant is added
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = test_emails["new_student"]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student_email in activities[activity_name]["participants"]
    
    def test_signup_activity_not_found_returns_404(self, client, test_emails):
        """
        Test signup to non-existent activity returns 404.
        
        Arrange: Use invalid activity name and test email
        Act: POST /activities/NonExistent/signup
        Assert: Returns 404 with "Activity not found" error
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        student_email = test_emails["new_student"]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_activity_full_returns_400(self, client, test_emails):
        """
        Test signup to full activity returns 400.
        
        Arrange: Use Tennis Club (capacity 10, currently has 1 participant)
                 Pre-fill activity to max capacity
        Act: POST signup when activity is full
        Assert: Returns 400 with "Activity is full" error
        """
        # Arrange
        activity_name = "Tennis Club"  # Max 10, currently 1 participant
        new_students = [test_emails[k] for k in ["new_student", "another_student", "third_student"]]
        
        # Fill the activity to capacity (need 9 more to reach 10)
        for i in range(9):
            email = f"fill.student{i}@mergington.edu"
            client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Activity should now be at capacity (10 participants)
        # Try to signup one more
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_students[0]}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Activity is full"
    
    def test_signup_duplicate_signup_returns_400(self, client, test_emails):
        """
        Test duplicate signup returns 400.
        
        Arrange: Student already signed up for an activity
        Act: POST signup for same activity with same email
        Assert: Returns 400 with "Student already signed up" error
        """
        # Arrange
        activity_name = "Programming Class"
        student_email = "emma@mergington.edu"  # Already signed up from initial data
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"
    
    def test_signup_new_student_to_different_activities(self, client, test_emails):
        """
        Test same student can signup to multiple activities.
        
        Arrange: Use test email and multiple activities
        Act: POST signup to Chess Club, then POST signup to Programming Class
        Assert: Both signups succeed and student appears in both activities
        """
        # Arrange
        student_email = test_emails["new_student"]
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act
        response1 = client.post(f"/activities/{activity1}/signup", params={"email": student_email})
        response2 = client.post(f"/activities/{activity2}/signup", params={"email": student_email})
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert student_email in activities[activity1]["participants"]
        assert student_email in activities[activity2]["participants"]
    
    def test_signup_updates_participant_list_in_subsequent_request(self, client, test_emails):
        """
        Test that signup persists in subsequent GET requests.
        
        Arrange: Get initial participant count, new student email
        Act: POST signup, then GET /activities
        Assert: Participant count increased by 1 in GET response
        """
        # Arrange
        activity_name = "Basketball Team"
        student_email = test_emails["new_student"]
        
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity_name]["participants"])
        
        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": student_email})
        updated_activities = client.get("/activities").json()
        updated_count = len(updated_activities[activity_name]["participants"])
        
        # Assert
        assert updated_count == initial_count + 1
        assert student_email in updated_activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success_for_activity(self, client, test_emails):
        """
        Test successful unregister from an activity.
        
        Arrange: Signup student, get activity and email
        Act: DELETE /activities/Chess Club/unregister with email
        Assert: Returns 200 and participant is removed
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = test_emails["new_student"]
        
        # First signup
        client.post(f"/activities/{activity_name}/signup", params={"email": student_email})
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student_email not in activities[activity_name]["participants"]
    
    def test_unregister_activity_not_found_returns_404(self, client, test_emails):
        """
        Test unregister from non-existent activity returns 404.
        
        Arrange: Use invalid activity name and test email
        Act: DELETE /activities/NonExistent/unregister
        Assert: Returns 404 with "Activity not found" error
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        student_email = test_emails["new_student"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_in_activity_returns_400(self, client, test_emails):
        """
        Test unregister when student not in activity returns 400.
        
        Arrange: Use test email for student who was never signed up
        Act: DELETE /activities/Chess Club/unregister
        Assert: Returns 400 with "Student not found in activity" error
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = test_emails["new_student"]  # Not signed up yet
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not found in activity"
    
    def test_unregister_original_participant_success(self, client):
        """
        Test unregister of an originally signed-up participant.
        
        Arrange: Use originally participant email from initial data
        Act: DELETE /activities/Chess Club/unregister
        Assert: Returns 200 and participant removed
        """
        # Arrange
        activity_name = "Chess Club"
        original_participant = "michael@mergington.edu"  # From initial data
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": original_participant}
        )
        
        # Assert
        assert response.status_code == 200
        
        activities = client.get("/activities").json()
        assert original_participant not in activities[activity_name]["participants"]
    
    def test_unregister_removes_only_specified_participant(self, client, test_emails):
        """
        Test that unregister only removes the specified participant.
        
        Arrange: Signup two students to same activity
        Act: DELETE unregister first student, GET /activities
        Assert: First student removed, second student still in list
        """
        # Arrange
        activity_name = "Gym Class"
        student1 = test_emails["new_student"]
        student2 = test_emails["another_student"]
        
        # Signup both
        client.post(f"/activities/{activity_name}/signup", params={"email": student1})
        client.post(f"/activities/{activity_name}/signup", params={"email": student2})
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student1}
        )
        
        # Assert
        assert response.status_code == 200
        
        activities = client.get("/activities").json()
        assert student1 not in activities[activity_name]["participants"]
        assert student2 in activities[activity_name]["participants"]
    
    def test_unregister_multiple_students_in_sequence(self, client, test_emails):
        """
        Test unregistering multiple students from same activity sequentially.
        
        Arrange: Signup three students to same activity
        Act: DELETE unregister each student one by one
        Assert: Each unregister succeeds and participant is removed
        """
        # Arrange
        activity_name = "Art Studio"
        students = [test_emails["new_student"], test_emails["another_student"], test_emails["third_student"]]
        
        # Signup all three
        for student_email in students:
            client.post(f"/activities/{activity_name}/signup", params={"email": student_email})
        
        # Act & Assert for each unregister
        for i, student_email in enumerate(students):
            response = client.delete(
                f"/activities/{activity_name}/unregister",
                params={"email": student_email}
            )
            assert response.status_code == 200
            
            # Verify student was removed
            activities = client.get("/activities").json()
            assert student_email not in activities[activity_name]["participants"]
            
            # Verify remaining students are still there
            for remaining_student in students[i+1:]:
                assert remaining_student in activities[activity_name]["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index_html(self, client):
        """
        Test root path redirects to static index page.
        
        Arrange: Get test client
        Act: GET / (with follow_redirects=False to see redirect)
        Assert: Returns redirect status (307 or 308) to /static/index.html
        """
        # Arrange
        expected_redirect_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code in [307, 308], \
            f"Expected redirect status (307/308), got {response.status_code}"
        assert response.headers["location"] == expected_redirect_location


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""
    
    def test_full_signup_flow_from_activities_to_signup_to_verify(self, client, test_emails):
        """
        Test complete signup flow: get activities, signup, verify in next request.
        
        Arrange: Get test client and student email
        Act: GET /activities -> POST signup -> GET /activities
        Assert: Participant appears in final GET request
        """
        # Arrange
        activity_name = "Music Band"
        student_email = test_emails["new_student"]
        
        # Act - Step 1: Get initial activities
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_count = len(initial_activities[activity_name]["participants"])
        
        # Act - Step 2: Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Act - Step 3: Get updated activities
        final_response = client.get("/activities")
        final_activities = final_response.json()
        final_count = len(final_activities[activity_name]["participants"])
        
        # Assert
        assert initial_response.status_code == 200
        assert signup_response.status_code == 200
        assert final_response.status_code == 200
        assert final_count == initial_count + 1
        assert student_email in final_activities[activity_name]["participants"]
    
    def test_full_unregister_flow_from_signup_to_unregister_to_verify(self, client, test_emails):
        """
        Test complete unregister flow: signup, unregister, verify in next request.
        
        Arrange: Signup student
        Act: DELETE unregister -> GET /activities
        Assert: Participant removed from final GET request
        """
        # Arrange
        activity_name = "Debate Club"
        student_email = test_emails["new_student"]
        
        # Pre-signup
        client.post(f"/activities/{activity_name}/signup", params={"email": student_email})
        activities_before = client.get("/activities").json()
        count_before = len(activities_before[activity_name]["participants"])
        
        # Act - Step 1: Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Act - Step 2: Get updated activities
        final_response = client.get("/activities")
        final_activities = final_response.json()
        count_after = len(final_activities[activity_name]["participants"])
        
        # Assert
        assert unregister_response.status_code == 200
        assert final_response.status_code == 200
        assert count_after == count_before - 1
        assert student_email not in final_activities[activity_name]["participants"]
    
    def test_multiple_students_signup_and_mixed_unregister(self, client, test_emails):
        """
        Test multiple students signing up and selectively unregistering.
        
        Arrange: Three student emails
        Act: Signup all -> Unregister first -> Signup another -> Unregister second
        Assert: Correct participants in activity at each step
        """
        # Arrange
        activity_name = "Science Club"
        student1 = test_emails["new_student"]
        student2 = test_emails["another_student"]
        student3 = test_emails["third_student"]
        students = [student1, student2, student3]
        
        # Act & Assert - Signup all three
        for student in students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student}
            )
            assert response.status_code == 200
        
        activities = client.get("/activities").json()
        for student in students:
            assert student in activities[activity_name]["participants"]
        
        # Act & Assert - Unregister first student
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student1}
        )
        assert response.status_code == 200
        
        activities = client.get("/activities").json()
        assert student1 not in activities[activity_name]["participants"]
        assert student2 in activities[activity_name]["participants"]
        assert student3 in activities[activity_name]["participants"]
        
        # Act & Assert - Unregister second student
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student2}
        )
        assert response.status_code == 200
        
        activities = client.get("/activities").json()
        assert student1 not in activities[activity_name]["participants"]
        assert student2 not in activities[activity_name]["participants"]
        assert student3 in activities[activity_name]["participants"]
