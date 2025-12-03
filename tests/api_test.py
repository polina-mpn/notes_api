import pytest
from fastapi.testclient import TestClient
from fastapi import status
from src.main import app


@pytest.fixture
def client(override_get_db):
    with TestClient(app=app, base_url="http://test") as client:
        yield client


def test_create_category(client):
    response = client.post("/api/categories/", json={"name": "Work"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Work"


def test_create_category_existing(client):
    response1 = client.post("/api/categories/", json={"name": "ExistingCat"})
    id1 = response1.json()["id"]

    response2 = client.post("/api/categories/", json={"name": "ExistingCat"})
    assert response2.status_code == status.HTTP_200_OK
    assert response2.json()["id"] == id1


def test_create_tag(client):
    response = client.post("/api/tags/", json={"name": "Urgent"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Urgent"


def test_create_note(client):
    category_response = client.post("/api/categories/", json={"name": "Work"})
    category_id = category_response.json()["id"]

    tag_response = client.post("/api/tags/", json={"name": "Important"})
    tag_id = tag_response.json()["id"]

    note_data = {
        "title": "Test Note",
        "content": "This is a test note.",
        "category_id": category_id,
        "tag_ids": [tag_id],
    }

    response = client.post("/api/notes/", json=note_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Test Note"
    assert response.json()["category"]["id"] == category_id
    assert response.json()["tags"][0]["id"] == tag_id
    assert isinstance(response.json()["tags"], list)


def test_get_notes(client):
    category_response = client.post("/api/categories/", json={"name": "Work"})
    category_id = category_response.json()["id"]
    client.post("/api/notes/", json={"title": "Note 1", "content": "...", "category_id": category_id})

    response = client.get("/api/notes/")
    assert response.status_code == status.HTTP_200_OK
    assert "items" in response.json()
    assert response.json()["total"] == 1
    assert len(response.json()["items"]) == 1


def test_get_note_by_id(client):
    category_response = client.post("/api/categories/", json={"name": "Work"})
    category_id = category_response.json()["id"]

    note_data = {
        "title": "Test Note",
        "content": "This is a test note.",
        "category_id": category_id,
    }
    note_response = client.post("/api/notes/", json=note_data)
    note_id = note_response.json()["id"]

    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == note_id


def test_get_note_not_found(client):
    response = client.get("/api/notes/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Note not found"


def test_update_note(client):
    category_response = client.post("/api/categories/", json={"name": "Work"})
    category_id = category_response.json()["id"]

    note_data = {
        "title": "Old Title",
        "content": "Old Content",
        "category_id": category_id,
    }
    note_response = client.post("/api/notes/", json=note_data)
    note_id = note_response.json()["id"]

    update_data = {"title": "Updated Test Note", "content": "New Content"}
    response = client.put(f"/api/notes/{note_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Test Note"
    assert response.json()["content"] == "New Content"
    assert response.json()["id"] == note_id


def test_delete_note(client):
    category_response = client.post("/api/categories/", json={"name": "Work"})
    category_id = category_response.json()["id"]

    note_data = {
        "title": "Note to Delete",
        "content": "...",
        "category_id": category_id,
    }
    note_response = client.post("/api/notes/", json=note_data)
    note_id = note_response.json()["id"]

    response = client.delete(f"/api/notes/{note_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Note deleted successfully"

    response_get = client.get(f"/api/notes/{note_id}")
    assert response_get.status_code == status.HTTP_404_NOT_FOUND