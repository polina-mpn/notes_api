from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Table,
    ForeignKey,
    Enum as SQLEnum,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from enum import Enum
from .database import Base


class NoteStatus(str, Enum):
    draft = "draft"
    active = "active"
    done = "done"
    postponed = "postponed"


class NotePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    notes = relationship("Note", back_populates="category")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    notes = relationship("Note", secondary=note_tags, back_populates="tags")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    is_important = Column(Boolean, default=False, nullable=False)
    status = Column(SQLEnum(NoteStatus), default=NoteStatus.active, nullable=False)
    priority = Column(SQLEnum(NotePriority), default=NotePriority.medium, nullable=False)
    reminder_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), nullable=True)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="notes")

    tags = relationship("Tag", secondary=note_tags, back_populates="notes")