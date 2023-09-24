from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
access_token = ""
refresh_token = ""
booking_id = 0


def test_frontpage():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API online"}


def test_nologin():
    protected_endpoints_get = ["/get_bookings", "/get_current_user"]
    protected_endpoints_delete = ["/remove_booking/1", "/delete_user"]
    for endpoint in protected_endpoints_get:
        response = client.get(endpoint)
        assert response.status_code == 403
    for endpoint in protected_endpoints_delete:
        response = client.delete(endpoint)
        assert response.status_code == 403


def test_register():
    response = client.get("/get_current_user")
    assert response.status_code == 403

    response = client.post("/register?name=test&password=test")
    assert response.status_code == 200

    response = response.json()
    assert response["status_code"] == 200


def test_login():
    global access_token, refresh_token
    response = client.post(
        "/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": "test", "password": "test"}
    )
    assert response.status_code == 200
    response = response.json()
    assert response["status_code"] == 200
    access_token = response["access_token"]
    refresh_token = response["refresh_token"]


def test_userinfo():
    response = client.get("/get_current_user")
    assert response.status_code == 403
    response = client.get("/get_current_user", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    response = response.json()
    assert response["status_code"] == 200
    assert response["user"]["username"] == "test"
    assert response["user"]["created_at"] == response["user"]["modified_at"]


def test_refresh_token():
    global access_token, refresh_token
    response = client.post(f"/refresh_token?token={refresh_token}")
    assert response.status_code == 200
    response = response.json()
    assert response["status_code"] == 200
    access_token = response["access_token"]
    refresh_token = response["refresh_token"]


def test_booking():
    global booking_id
    response = client.post(
        "/create_booking?start_time=01-09-2023%2000:00:00&end_time=01-09-2023%2001:00:00&comment=1",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    response = response.json()
    assert response["status_code"] == 200
    booking_id = response["booking_id"]
    response = client.get("/get_bookings",
                          headers={"Authorization": f"Bearer {access_token}"}, )
    assert response.status_code == 200
    response = response.json()
    assert response["status_code"] == 200
    assert len(response["bookings"]) == 1
    assert response["bookings"][0]["id"] == booking_id
    assert response["bookings"][0]["start_time"] == "01-09-2023 00:00:00"
    assert response["bookings"][0]["end_time"] == "01-09-2023 01:00:00"
    assert response["bookings"][0]["comment"] == "1"


def test_user_edit():
    response = client.patch("/update_user?username=test1&password=test1",
                            headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    response = response.json()
    assert response["status_code"] == 200


def test_delete_booking():
    response = client.delete(f"/remove_booking/{booking_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    response = client.get("/get_bookings", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    response = response.json()
    assert response["status_code"] == 200
    assert len(response["bookings"]) == 0


def test_delete_user():
    response = client.delete("/delete_user", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
