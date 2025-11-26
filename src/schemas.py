from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
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
    title: str = Field(..., json_schema_extra={'example': "Сдать проект"})
    content: Optional[str] = Field(None, json_schema_extra={'example': "Сделать README и тесты"})
    is_important: bool = False
    status: NoteStatus = NoteStatus.active
    priority: NotePriority = NotePriority.medium
    reminder_date: Optional[datetime] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = []


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