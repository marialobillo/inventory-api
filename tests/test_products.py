from fastapi.testclient import TestClient
from uuid import uuid4
from app.main import create_app

def client():
    return TestClient(create_app())

def test_create_and_get_product():
    c = client()
    pid = str(uuid4())
    r = c.post("/products", json={"id": pid, "name": "Tea", "price": 5, "stock": 1})
    assert r.status_code in (200, 201)

    g = c.get(f"/products/{pid}")
    assert g.status_code == 200
    assert g.json()["name"] == "Tea"

def test_duplicate_returns_409():
    c = client()
    pid = str(uuid4())
    c.post("/products", json={"id": pid, "name": "A", "price": 1, "stock": 1})
    dup = c.post("/products", json={"id": pid, "name": "B", "price": 2, "stock": 2})
    assert dup.status_code == 409
    assert dup.json()["error"] == "AlreadyExists"

def test_validation_400():
    c = client()
    res = c.post("/products", json={"id": "not-uuid", "name": "", "price": -1, "stock": -1})
    assert res.status_code == 400
    assert res.json()["error"] == "ValidationError"

def test_patch_update_and_notfound_and_invalid():
    c = client()
    pid = str(uuid4())
    c.post("/products", json={"id": pid, "name": "Tea", "price": 5, "stock": 1})

    upd = c.patch(f"/products/{pid}", json={"stock": 3})
    assert upd.status_code == 200
    assert upd.json()["stock"] == 3

    invalid = c.patch(f"/products/{pid}", json={"price": -1})
    assert invalid.status_code == 400
    assert invalid.json()["error"] == "ValidationError"

    missing = c.patch(f"/products/{uuid4()}", json={"stock": 1})
    assert missing.status_code == 404
    assert missing.json()["error"] == "NotFound"

def test_delete_204_and_notfound():
    c = client()
    pid = str(uuid4())
    c.post("/products", json={"id": pid, "name": "Tea", "price": 5, "stock": 1})
    d = c.delete(f"/products/{pid}")
    assert d.status_code == 204
    g = c.get(f"/products/{pid}")
    assert g.status_code == 404
