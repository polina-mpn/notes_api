from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import database, crud, schemas, models
from datetime import datetime
from ..schemas import NoteStatus, NotePriority

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_tags_and_get_ids(db: Session, tags_csv: str) -> List[int]:
    if not tags_csv:
        return []
    names = [t.strip() for t in tags_csv.split(",") if t.strip()]
    ids = []
    for name in names:
        existing = crud.get_tag_by_name(db, name)
        if existing:
            ids.append(existing.id)
        else:
            new = crud.create_tag(db, schemas.TagCreate(name=name))
            ids.append(new.id)
    return ids


def ensure_category_and_get_id(db: Session, category_name: Optional[str]) -> Optional[int]:
    if not category_name:
        return None
    existing = crud.get_category_by_name(db, category_name)
    if existing:
        return existing.id
    new = crud.create_category(db, schemas.CategoryCreate(name=category_name))
    return new.id


@router.get("/notes", include_in_schema=False)
def notes_list(request: Request, db: Session = Depends(get_db),
               status: Optional[str] = None,
               important: Optional[str] = None,
               search: Optional[str] = None):
    important_bool = None
    if important is not None and important.lower() in ('true', '1', 'on', 'yes', 't'):
        important_bool = True

    print(f"DEBUG: important_str={important}, important_bool={important_bool}")

    status_enum = None
    if status and status.strip():
        try:
            status_enum = models.NoteStatus(status.strip())
        except ValueError:
            status_enum = None

    notes = crud.get_notes_filtered(db, status=status_enum, important=important_bool, search=search)
    categories = crud.get_categories(db)
    return templates.TemplateResponse("index.html", {"request": request, "notes": notes, "categories": categories})


@router.get("/notes/create", include_in_schema=False)
def note_create_form(request: Request, db: Session = Depends(get_db)):
    categories = crud.get_categories(db)
    tags = crud.get_tags(db)
    return templates.TemplateResponse("note_create.html", {"request": request, "categories": categories, "tags": tags})


@router.post("/notes/create", include_in_schema=False)
def note_create(
    title: str = Form(...),
    content: str = Form(""),
    category_name: str = Form(""),
    tags: str = Form(""),  # comma-separated tag names
    is_important: Optional[str] = Form(None),
    status: NoteStatus = Form(NoteStatus.active.value),
    priority: NotePriority = Form(NotePriority.medium.value),
    reminder_date: str = Form(None),
    db: Session = Depends(get_db)
):
    category_id = ensure_category_and_get_id(db, category_name.strip() or None)
    tag_ids = ensure_tags_and_get_ids(db, tags)

    rdate = None
    if reminder_date:
        try:
            rdate = datetime.fromisoformat(reminder_date)
        except Exception:
            rdate = None

    note_in = schemas.NoteCreate(
        title=title,
        content=content,
        is_important=bool(is_important),
        status=status,
        priority=priority,
        reminder_date=rdate,
        category_id=category_id,
        tag_ids=tag_ids
    )
    crud.create_note(db, note_in)
    return RedirectResponse(url="/notes", status_code=303)


@router.get("/notes/{note_id}", include_in_schema=False)
def note_view(request: Request, note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        return RedirectResponse(url="/notes")
    return templates.TemplateResponse("note_view.html", {"request": request, "note": note})


@router.get("/notes/{note_id}/edit", include_in_schema=False)
def note_edit_form(request: Request, note_id: int, db: Session = Depends(get_db)):

    note = crud.get_note(db, note_id)
    if not note:
        return RedirectResponse(url="/notes")
    categories = crud.get_categories(db)
    tags = crud.get_tags(db)
    tag_names = ", ".join([t.name for t in note.tags])
    return templates.TemplateResponse("note_edit.html", {"request": request, "note": note, "categories": categories, "tags": tags, "tag_names": tag_names})


@router.post("/notes/{note_id}/edit", include_in_schema=False)
def note_edit(
    note_id: int,
    title: str = Form(...),
    content: str = Form(""),
    category_name: str = Form(""),
    tags: str = Form(""),
    is_important: Optional[str] = Form(None),
    status: NoteStatus = Form(NoteStatus.active.value),
    priority: NotePriority = Form(NotePriority.medium.value),
    reminder_date: str = Form(None),
    db: Session = Depends(get_db)
):
    category_id = ensure_category_and_get_id(db, category_name.strip() or None)
    tag_ids = ensure_tags_and_get_ids(db, tags)
    rdate = None
    if reminder_date:
        try:
            rdate = datetime.fromisoformat(reminder_date)
        except Exception:
            rdate = None

    note_update = schemas.NoteUpdate(
        title=title,
        content=content,
        is_important=bool(is_important),
        status=status,
        priority=priority,
        reminder_date=rdate,
        category_id=category_id,
        tag_ids=tag_ids
    )
    crud.update_note(db, note_id, note_update)
    return RedirectResponse(url=f"/notes/{note_id}", status_code=303)


@router.post("/notes/{note_id}/delete", include_in_schema=False)
def note_delete(note_id: int, db: Session = Depends(get_db)):
    crud.delete_note(db, note_id)
    return RedirectResponse(url="/notes", status_code=303)