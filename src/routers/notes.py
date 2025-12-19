from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from .. import schemas, crud, models, database
from ..database import get_db

router = APIRouter(prefix="/api", tags=["notes"])


@router.post("/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    existing = crud.get_category_by_name(db, category.name)
    if existing:
        return existing
    return crud.create_category(db, category)


@router.get("/categories/", response_model=List[schemas.Category])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)


@router.post("/tags/", response_model=schemas.Tag)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    existing = crud.get_tag_by_name(db, tag.name)
    if existing:
        return existing
    return crud.create_tag(db, tag)


@router.get("/tags/", response_model=List[schemas.Tag])
def list_tags(db: Session = Depends(get_db)):
    return crud.get_tags(db)


@router.post("/notes/", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db, note)

@router.get("/notes/", response_model=schemas.PaginatedNotes) # <--- ИЗМЕНЕНИЕ
def read_notes(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(100, ge=1, le=1000, description="Limit"),
    category_id: Optional[int] = Query(None),
    tag_id: Optional[int] = Query(None),
    status: Optional[models.NoteStatus] = Query(None),
    priority: Optional[models.NotePriority] = Query(None),
    important: Optional[bool] = Query(None),
    before: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
):

    # TODO: КРИТИЧНО! Добавить skip и limit в вызов функции для корректной пагинации
    # Сейчас параметры объявлены, но не используются - загружаются ВСЕ записи!
    # Исправление:
    # notes = crud.get_notes_filtered(
    #     db,
    #     skip=skip,        # <-- Добавить эту строку
    #     limit=limit,      # <-- Добавить эту строку
    #     category_id=category_id,
    #     ...
    # )
    notes = crud.get_notes_filtered(
        db,
        category_id=category_id,
        tag_id=tag_id,
        status=status,
        important=important,
        before=before,
        search=search,
        priority=priority,
    )

    total = crud.count_notes_filtered(
        db,
        category_id=category_id,
        tag_id=tag_id,
        status=status,
        important=important,
        before=before,
        search=search,
        priority=priority,
    )

    return {
        "items": notes,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/notes/{note_id}", response_model=schemas.Note)
def read_note(note_id: int, db: Session = Depends(get_db)):
    db_note = crud.get_note(db, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note


@router.put("/notes/{note_id}", response_model=schemas.Note)
def put_note(note_id: int, note: schemas.NoteUpdate, db: Session = Depends(get_db)):
    updated = crud.update_note(db, note_id, note)
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated


@router.delete("/notes/{note_id}")
def remove_note(note_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_note(db, note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}