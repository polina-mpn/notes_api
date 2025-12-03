from sqlalchemy.orm import Session
from datetime import datetime, UTC
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
import logging

from . import models, schemas

logger = logging.getLogger(__name__)

def get_category_by_name(db: Session, name: str) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.name == name).first()


def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    db_cat = models.Category(name=category.name)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


def get_categories(db: Session) -> List[models.Category]:
    return db.query(models.Category).all()


def get_tag_by_name(db: Session, name: str) -> Optional[models.Tag]:
    return db.query(models.Tag).filter(models.Tag.name == name).first()


def create_tag(db: Session, tag: schemas.TagCreate) -> models.Tag:
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def get_tags(db: Session) -> List[models.Tag]:
    return db.query(models.Tag).all()


def create_note(db: Session, note_in: schemas.NoteCreate) -> models.Note:
    try:
        db_note = models.Note(
            title=note_in.title,
            content=note_in.content,
            is_important=note_in.is_important,
            status=note_in.status,
            priority=note_in.priority,
            reminder_date=note_in.reminder_date,
            category_id=note_in.category_id,
        )

        if note_in.tag_ids:
            tags = db.query(models.Tag).filter(models.Tag.id.in_(note_in.tag_ids)).all()
            if len(tags) != len(note_in.tag_ids):
                raise HTTPException(400, "Some tag IDs not found")
            db_note.tags = tags

        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error: {e}")
        raise HTTPException(400, "Database constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(500, "Database error")


def get_note(db: Session, note_id: int) -> Optional[models.Note]:
    return db.query(models.Note).filter(models.Note.id == note_id).first()


def delete_note(db: Session, note_id: int) -> Optional[models.Note]:
    db_note = get_note(db, note_id)
    if db_note:
        db.delete(db_note)
        db.commit()
    return db_note


def update_note(db: Session, note_id: int, note_data: schemas.NoteUpdate) -> Optional[models.Note]:
    db_note = get_note(db, note_id)
    if not db_note:
        return None

    for field, value in note_data.model_dump(exclude_unset=True).items():
        if field == "tag_ids":
            if value is None:
                db_note.tags = []
            else:
                tags = db.query(models.Tag).filter(models.Tag.id.in_(value)).all()
                db_note.tags = tags
        else:
            setattr(db_note, field, value)

    db_note.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(db_note)
    return db_note


def get_notes_filtered(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    status: Optional[models.NoteStatus] = None,
    important: Optional[bool] = None,
    before: Optional[datetime] = None,
    search: Optional[str] = None,
    priority: Optional[models.NotePriority] = None,
) -> List[models.Note]:
    q = db.query(models.Note)

    if category_id is not None:
        q = q.filter(models.Note.category_id == category_id)

    if tag_id is not None:
        q = q.join(models.Note.tags).filter(models.Tag.id == tag_id)

    if status is not None:
        q = q.filter(models.Note.status == status)

    if priority is not None:
        q = q.filter(models.Note.priority == priority)

    if important is True:
        q = q.filter(models.Note.is_important == True)

    if before is not None:
        q = q.filter(models.Note.reminder_date <= before)

    if search:
        search_escaped = search.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        like = f"%{search_escaped}%"
        q = q.outerjoin(models.Note.tags).filter(
            (models.Note.title.ilike(like, escape='\\')) |
            (models.Note.content.ilike(like, escape='\\')) |
            (models.Tag.name.ilike(like, escape='\\'))
        ).distinct()

    return q.order_by(models.Note.created_at.desc()).offset(skip).limit(limit).all()

def count_notes_filtered(
    db: Session,
    category_id: int = None,
    tag_id: int = None,
    status: models.NoteStatus = None,
    important: bool = None,
    before: datetime = None,
    search: str = None,
    priority: models.NotePriority = None,
):
    query = db.query(models.Note)

    if category_id:
        query = query.filter(models.Note.category_id == category_id)
    if tag_id:
        query = query.join(models.Note.tags).filter(models.Tag.id == tag_id)
    if status:
        query = query.filter(models.Note.status == status)
    if priority:
        query = query.filter(models.Note.priority == priority)
    if important is not None:
        query = query.filter(models.Note.important == important)
    if before:
        query = query.filter(models.Note.created_at < before)
    if search:
        query = query.filter(models.Note.title.ilike(f"%{search}%"))

    return query.count()