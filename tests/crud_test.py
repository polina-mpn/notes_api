import pytest
from src import crud, models, schemas

def test_create_category(db):
    category_data = schemas.CategoryCreate(name="Work")
    category = crud.create_category(db, category_data)
    assert category.name == "Work"


def test_create_tag(db):
    tag_data = schemas.TagCreate(name="Urgent")
    tag = crud.create_tag(db, tag_data)
    assert tag.name == "Urgent"


def test_create_note(db):
    category = crud.create_category(db, schemas.CategoryCreate(name="Work"))
    tag = crud.create_tag(db, schemas.TagCreate(name="Important"))
    note_data = schemas.NoteCreate(
        title="Test Note",
        content="This is a test note.",
        category_id=category.id,
        tag_ids=[tag.id],
    )
    note = crud.create_note(db, note_data)
    assert note.title == "Test Note"
    assert note.category.name == "Work"
    assert note.tags[0].name == "Important"


def test_get_note(db):
    category = crud.create_category(db, schemas.CategoryCreate(name="Work"))
    tag = crud.create_tag(db, schemas.TagCreate(name="Important"))
    note_data = schemas.NoteCreate(
        title="Test Note",
        content="This is a test note.",
        category_id=category.id,
        tag_ids=[tag.id],
    )
    note = crud.create_note(db, note_data)
    retrieved_note = crud.get_note(db, note.id)
    assert retrieved_note.id == note.id
    assert retrieved_note.title == "Test Note"


def test_update_note(db):
    category = crud.create_category(db, schemas.CategoryCreate(name="Work"))
    note_data = schemas.NoteCreate(
        title="Test Note",
        content="This is a test note.",
        category_id=category.id,
    )
    note = crud.create_note(db, note_data)

    updated_data = schemas.NoteUpdate(title="Updated Test Note")
    updated_note = crud.update_note(db, note.id, updated_data)
    assert updated_note.title == "Updated Test Note"


def test_delete_note(db):
    category = crud.create_category(db, schemas.CategoryCreate(name="Work"))
    note_data = schemas.NoteCreate(
        title="Test Note",
        content="This is a test note.",
        category_id=category.id,
    )
    note = crud.create_note(db, note_data)
    deleted_note = crud.delete_note(db, note.id)
    assert deleted_note.id == note.id
