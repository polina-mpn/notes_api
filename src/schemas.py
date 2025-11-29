from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime, UTC
from enum import Enum

class NoteStatus(str, Enum):
    draft = "draft"
    active = "active"
    done = "done"
    postponed = "postponed"


class NotePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TagBase(BaseModel):
    name: str = Field(..., json_schema_extra={'example': "учёба"})


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    name: str = Field(..., json_schema_extra={'example': "учёба"})


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = Field(None, max_length=5000)
    is_important: bool = False
    status: NoteStatus = NoteStatus.active
    priority: NotePriority = NotePriority.medium
    reminder_date: Optional[datetime] = Field(None, description="Reminder date (future)")
    category_id: Optional[int] = Field(None, ge=1)
    tag_ids: Optional[List[int]] = Field(default_factory=list)

    @field_validator('title', 'content')
    def not_empty_string(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Field cannot be empty or whitespace')
        return v.strip() if v else v

    @field_validator('reminder_date')
    def reminder_in_future(cls, v):
        if v:
            if v.tzinfo is None:
                v = v.replace(tzinfo=UTC)
            if v < datetime.now(UTC):
                raise ValueError("reminder must be in the future")
        return v

    @field_validator('tag_ids')
    def unique_tags(cls, v):
        if v and len(v) != len(set(v)):
            raise ValueError('Tag IDs must be unique')
        return v


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator('name')
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

    @field_validator('name')
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_important: Optional[bool] = None
    status: Optional[NoteStatus] = None
    priority: Optional[NotePriority] = None
    reminder_date: Optional[datetime] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[Category] = None
    tags: List[Tag] = []

    model_config = ConfigDict(from_attributes=True)


class PaginatedNotes(BaseModel):
    items: List[Note]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)