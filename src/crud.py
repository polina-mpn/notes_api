from sqlalchemy.orm import Session
from datetime import datetime, UTC
from typing import List, Optional

from . import models, schemas


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
        db_note.tags = tags

    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


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
        like = f"%{search}%"
        q = q.outerjoin(models.Note.tags).filter(
            (models.Note.title.ilike(like)) | (models.Note.content.ilike(like)) | (models.Tag.name.ilike(like))
        ).distinct()

    return q.order_by(models.Note.created_at.desc()).all()