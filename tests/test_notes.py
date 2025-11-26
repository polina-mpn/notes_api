import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import Base, engine, SessionLocal
from src import models

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def prepare_db():
    # recreate DB for tests
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # add some initial data
    db = SessionLocal()
    cat = models.Category(name="test-cat")
    tag = models.Tag(name="test-tag")
    db.add(cat)
    db.add(tag)
    db.commit()
    db.refresh(cat)
    db.refresh(tag)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_note():
    # create note with category_id and tag_ids
    response = client.post(
        "/api/notes/",
        json={
            "title": "Test note",
            "content": "Content",
            "is_important": True,
            "status": "active",
            "priority": "high",
            "category_id": 1,
            "tag_ids": [1],
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Test note"
    assert data["is_important"] is True
    assert data["category"]["id"] == 1
    assert len(data["tags"]) == 1


def test_get_notes_filter_by_tag():
    # filter by tag_id
    response = client.get("/api/notes/?tag_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["tags"][0]["name"] == "test-tag"


def test_update_note_partial():
    # partial update: change title and unmark importance
    response = client.put("/api/notes/1", json={"title": "Updated", "is_important": False})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["is_important"] is False