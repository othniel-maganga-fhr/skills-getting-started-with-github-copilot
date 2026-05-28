def test_signup_then_unregister_reflects_immediate_state(client):
    activity_name = "Programming Class"
    email = "flow.student@mergington.edu"

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert signup_response.status_code == 200

    activities_after_signup = client.get("/activities").json()
    assert email in activities_after_signup[activity_name]["participants"]

    unregister_response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert unregister_response.status_code == 200

    activities_after_unregister = client.get("/activities").json()
    assert email not in activities_after_unregister[activity_name]["participants"]


def test_duplicate_signup_prevention_across_sequential_calls(client):
    activity_name = "Science Club"
    email = "sequential.student@mergington.edu"

    first_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    second_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_capacity_boundary_last_slot_then_overflow(client):
    activity_name = "Debate Team"
    email_for_last_slot = "last.slot@mergington.edu"
    email_overflow = "overflow.slot@mergington.edu"

    activities = client.get("/activities").json()
    current_count = len(activities[activity_name]["participants"])
    max_participants = activities[activity_name]["max_participants"]

    for i in range(current_count, max_participants - 1):
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": f"boundary{i}@mergington.edu"},
        )
        assert response.status_code == 200

    last_slot_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email_for_last_slot},
    )
    overflow_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email_overflow},
    )

    assert last_slot_response.status_code == 200
    assert overflow_response.status_code == 400
    assert overflow_response.json()["detail"] == "Activity is full"
