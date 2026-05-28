def test_signup_success_adds_participant(client):
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post("/activities/Unknown Club/signup", params={"email": "any@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_participant(client):
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_400_when_activity_is_full(client):
    activity_name = "Chess Club"
    activities = client.get("/activities").json()

    max_participants = activities[activity_name]["max_participants"]
    current_count = len(activities[activity_name]["participants"])

    for i in range(current_count, max_participants):
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": f"fill{i}@mergington.edu"},
        )
        assert response.status_code == 200

    overflow_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "overflow@mergington.edu"},
    )

    assert overflow_response.status_code == 400
    assert overflow_response.json()["detail"] == "Activity is full"
