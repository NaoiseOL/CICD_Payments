import pytest

def booking_payload(bid=11, first_name="Naoise", surname="OLoughlin", start_Date="08/10/2025",end_Date="09/10/2025"):
    return {"booking_id":bid, "first_name":first_name, "surname":surname,"start_Date":start_Date, "end_Date":end_Date}

def test_create_booking_ok(client):
    r = client.post("/api/bookings", json=booking_payload())
    assert r.status_code == 201
    data=r.json()
    assert data ["booking_id"] == 11
    assert data ["first_name"] == "Naoise"

def test_duplicate_booking_id_conflict(client):
    client.post("/api/bookings", json=booking_payload(bid=12))
    r = client.post("/api/bookings", json=booking_payload(bid=12))
    assert r.status_code == 409
    assert "exists" in r.json()["detail"].lower()

def test_get_booking_404(client):
    r = client.get("/api/booking/999")
    assert r.status_code == 404

def test_delete_then_404(client):
    client.post("/api/bookings", json=booking_payload(bid=13))
    r1 = client.delete("/api/bookings/13")
    assert r1.status_code == 204
    r2 = client.delete("/api/bookings/13")
    assert r2.status_code == 404

def test_booking_update(client):
    client.post("/api/bookings", json=booking_payload(bid=15))

    r=client.put("/api/bookings/15", json=booking_payload(bid=15, first_name="John", surname="Doe"))

    assert r.status_code == 200
    data=r.json()

    assert data["booking_id"] == 15
    assert data["first_name"] == "John"
    assert data["surname"] == "Doe"

def test_booking_update_404(client):
    r = client.put("/api/bookings/999", json=booking_payload(bid=15, first_name="John", surname="Doe"))

    assert r.status_code == 404