"""Tests for the main module."""
from fastapi.testclient import TestClient

from .main import app

ITEMS_ROUTE = "/items/"

client = TestClient(app)


def test_read_item() -> None:
    """Test the GET /items/{item_id} endpoint."""
    response = client.get("/items/foo", headers={"X-Token": "coneofsilence"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "foo",
        "title": "Foo",
        "description": "There goes my hero",
    }


def test_read_item_bad_token() -> None:
    """Test the GET /items/{item_id} endpoint with a bad token."""
    response = client.get("/items/foo", headers={"X-Token": "hailhydra"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid X-Token header"}


def test_read_inexistent_item() -> None:
    """Test the GET /items/{item_id} endpoint with an inexistent item."""
    response = client.get("/items/baz", headers={"X-Token": "coneofsilence"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_create_item() -> None:
    """Test the POST /items/ endpoint."""
    response = client.post(
        ITEMS_ROUTE,
        headers={"X-Token": "coneofsilence"},
        json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": "foobar",
        "title": "Foo Bar",
        "description": "The Foo Barters",
    }


def test_create_item_bad_token() -> None:
    """Test the POST /items/ endpoint with a bad token."""
    response = client.post(
        ITEMS_ROUTE,
        headers={"X-Token": "hailhydra"},
        json={"id": "bazz", "title": "Bazz", "description": "Drop the bazz"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid X-Token header"}


def test_create_existing_item() -> None:
    """Test the POST /items/ endpoint with an existing item."""
    response = client.post(
        ITEMS_ROUTE,
        headers={"X-Token": "coneofsilence"},
        json={
            "id": "foo",
            "title": "The Foo ID Stealers",
            "description": "There goes my stealer",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Item already exists"}
