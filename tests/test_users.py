import pytest

def user_payload(uid=1, first_name="Naoise", surname="OLoughlin", age=25, email="naoiseol123@gmail.com", phoneNo="0860378167",booking_number="01"):
    return {"user_id":uid, "first_name":first_name, "surname":surname, "age": age, "email":email, "phoneNo":phoneNo,"booking_number":booking_number}

def test_create_user_ok(client):
    r = client.post("/api/users", json=user_payload())
    assert r.status_code == 201
    data = r.json()
    assert data["user_id"] == 1
    assert data["first_name"] == "Naoise"