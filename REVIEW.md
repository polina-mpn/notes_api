# 📋 Code Review: Notes API (FastNotes)

**Оценка:** 8.5/10 ⭐  
**Дата:** 25 ноября 2025

---

## ✅ Сильные стороны

1. **Отличная архитектура** - профессиональное разделение на модули
2. **Продуманная модель данных** - Category, Tag, Note с relationships
3. **Современный FastAPI** - правильное использование роутеров, схем Pydantic v2
4. **Enum для статусов** - типобезопасные статусы и приоритеты
5. **Alembic миграции** - правильный подход к версионированию БД
6. **Фильтрация и поиск** - сложные запросы с multiple условиями
7. **Frontend** - есть веб-интерфейс на Jinja2
8. **Хороший README** - детальная документация
9. **Тесты** - есть базовое тестирование
10. **Config файл** - вынесена конфигурация

**Это один из лучших проектов!** 🎉

---

## 🔴 Критические проблемы (TODO - исправить)

### 1. **TODO: Устаревшее создание таблиц**
**Файл:** `src/main.py`, строка 8

```python
models.Base.metadata.create_all(bind=database.engine)
```

❌ **Проблема:** Игнорируются миграции Alembic.

✅ **Решение:** Удалите эту строку, используйте только:
```bash
alembic upgrade head
```

---

### 2. **TODO: SQL Injection риск в поиске**
**Файл:** `src/crud.py`, строка 133

```python
if search:
    like = f"%{search}%"
    q = q.filter(
        (models.Note.title.ilike(like)) | 
        (models.Note.content.ilike(like)) | 
        (models.Tag.name.ilike(like))
    )
```

❌ **Проблема:** Спецсимволы `%` и `_` не экранируются.

✅ **Исправление:**
```python
if search:
    # Экранируем спецсимволы LIKE
    search_escaped = search.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    like = f"%{search_escaped}%"
    q = q.outerjoin(models.Note.tags).filter(
        (models.Note.title.ilike(like, escape='\\')) | 
        (models.Note.content.ilike(like, escape='\\')) | 
        (models.Tag.name.ilike(like, escape='\\'))
    ).distinct()
```

---

### 3. **TODO: Отсутствует пагинация**
**Файл:** `src/routers/notes.py`, строка 53

❌ **Проблема:** При большом количестве записей загружаются все.

✅ **Исправление:**
```python
from fastapi import Query

@router.get("/notes/", response_model=List[schemas.Note])
def read_notes(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(100, ge=1, le=1000, description="Limit"),
    category_id: Optional[int] = Query(None),
    # ... остальные параметры
):
    notes = crud.get_notes_filtered(
        db, 
        skip=skip, 
        limit=limit,
        category_id=category_id,
        # ...
    )
    total = crud.count_notes_filtered(db, category_id=category_id, ...)
    
    return {
        "items": notes,
        "total": total,
        "skip": skip,
        "limit": limit
    }

# В crud.py
def get_notes_filtered(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    # ... фильтры
) -> List[models.Note]:
    q = db.query(models.Note)
    # ... фильтры ...
    return q.order_by(models.Note.created_at.desc()).offset(skip).limit(limit).all()
```

---

### 4. **TODO: Нет валидации входных данных**
**Файл:** `src/schemas.py`

❌ **Проблема:** Нет ограничений на длину, пустые значения.

✅ **Исправление:**
```python
from pydantic import BaseModel, Field, validator

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = Field(None, max_length=5000)
    is_important: bool = False
    status: NoteStatus = NoteStatus.active
    priority: NotePriority = NotePriority.medium
    reminder_date: Optional[datetime] = Field(None, description="Reminder date (future)")
    category_id: Optional[int] = Field(None, ge=1)
    tag_ids: Optional[List[int]] = Field(default_factory=list)
    
    @validator('title', 'content')
    def not_empty_string(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Field cannot be empty or whitespace')
        return v.strip() if v else v
    
    @validator('reminder_date')
    def reminder_in_future(cls, v):
        if v and v < datetime.now(UTC):
            raise ValueError('Reminder date must be in the future')
        return v
    
    @validator('tag_ids')
    def unique_tags(cls, v):
        if v and len(v) != len(set(v)):
            raise ValueError('Tag IDs must be unique')
        return v

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    
    @validator('name')
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    
    @validator('name')
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
```

---

### 5. **TODO: Нет обработки ошибок БД**
**Файл:** `src/crud.py`

Добавьте try/except:
```python
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

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
```

---

### 6. **TODO: Дублирование get_db()**
**Файл:** `src/routers/notes.py`, строка 12

У вас есть `get_db()` в роутере И в `database.py`. Используйте один:

```python
# Удалите из notes.py
# def get_db(): ...

# Используйте импорт
from ..database import get_db
```

Или создайте `src/dependencies.py`:
```python
from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 💡 Рекомендации (желательно)

### 1. Добавьте CORS
```python
# src/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Добавьте логирование
```python
# src/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
def startup():
    logger.info("Application started")
```

### 3. Добавьте middleware для логирования запросов
```python
# src/main.py
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.3f}s "
        f"with status {response.status_code}"
    )
    return response
```

### 4. Используйте lifespan вместо on_event
```python
# src/main.py (FastAPI 0.121+)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(title=config.APP_NAME, lifespan=lifespan)
```

### 5. Добавьте rate limiting
```python
# pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/notes/")
@limiter.limit("10/minute")
def create_note(...):
    ...
```

### 6. Расширьте тесты
```python
# tests/test_notes.py
import pytest
from fastapi.testclient import TestClient

def test_create_note_with_tags(client, db):
    # Создаём теги
    tag1 = client.post("/api/tags/", json={"name": "важно"}).json()
    tag2 = client.post("/api/tags/", json={"name": "работа"}).json()
    
    # Создаём заметку с тегами
    response = client.post("/api/notes/", json={
        "title": "Test",
        "content": "Content",
        "tag_ids": [tag1["id"], tag2["id"]]
    })
    assert response.status_code == 200
    note = response.json()
    assert len(note["tags"]) == 2

def test_search_notes(client):
    # Создаём заметку
    client.post("/api/notes/", json={"title": "Python", "content": "FastAPI"})
    
    # Ищем
    response = client.get("/api/notes/?search=Python")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_filter_by_status(client):
    response = client.get("/api/notes/?status=active")
    assert response.status_code == 200

def test_validation_empty_title(client):
    response = client.post("/api/notes/", json={"title": "", "content": "test"})
    assert response.status_code == 422  # Validation error
```

### 7. Добавьте .env support
```python
# pip install python-dotenv

# src/config.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'notes.db'}")
APP_NAME = os.getenv("APP_NAME", "FastNotes API")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
```

Создайте `.env`:
```bash
DATABASE_URL=sqlite:///./notes.db
APP_NAME=FastNotes API
DEBUG=True
```

### 8. Добавьте Swagger описания
```python
# src/main.py
app = FastAPI(
    title="FastNotes API",
    description="API для управления заметками с тегами, категориями и приоритетами",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# В роутерах
@router.post(
    "/notes/", 
    response_model=schemas.Note,
    summary="Создать заметку",
    description="Создаёт новую заметку с тегами и категорией"
)
def create_note(...):
```

### 9. Добавьте background tasks для напоминаний
```python
from fastapi import BackgroundTasks

def send_reminder(note_id: int, title: str):
    # Логика отправки напоминания (email, push и т.д.)
    logger.info(f"Reminder sent for note {note_id}: {title}")

@router.post("/notes/")
def create_note(
    note: schemas.NoteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_note = crud.create_note(db, note)
    
    if note.reminder_date:
        # Планируем напоминание
        delay = (note.reminder_date - datetime.now(UTC)).total_seconds()
        if delay > 0:
            # В реальном приложении используйте Celery или APScheduler
            logger.info(f"Scheduled reminder for note {db_note.id}")
    
    return db_note
```

---

## 📊 Оценка

| Критерий | Балл | Комментарий |
|----------|------|-------------|
| Архитектура | 10/10 | Профессиональная структура |
| Функциональность | 9/10 | Богатый функционал |
| Модель данных | 9/10 | Продуманные отношения |
| Код качество | 8/10 | Чистый, но нет валидации |
| Безопасность | 7/10 | SQL injection в поиске |
| Тестирование | 6/10 | Базовые тесты |
| Документация | 9/10 | Отличный README |

**Общая оценка: 8.5/10** ⭐

---

## 🎯 План исправлений

### Высокий приоритет (1 час):
1. ✅ Удалить `Base.metadata.create_all()` из main.py
2. ✅ Исправить SQL injection в поиске
3. ✅ Добавить валидацию в schemas
4. ✅ Убрать дублирование get_db()

### Средний приоритет (2 часа):
5. Добавить пагинацию
6. Добавить обработку ошибок БД
7. Добавить логирование
8. Добавить CORS

### Низкий приоритет (опционально):
9. Rate limiting
10. Расширить тесты
11. Background tasks для напоминаний
12. .env support

---

## 💬 Заключение

**Отличный проект!** 🎉 Это один из лучших студенческих проектов, которые я видел. Профессиональная архитектура, продуманная модель данных, rich функционал.

Основные моменты для исправления:
- SQL injection в поиске (критично)
- Отсутствие пагинации (важно)
- Валидация входных данных (важно)
- Обработка ошибок БД (желательно)

После исправления критических моментов проект будет готов даже для небольшого production! Продолжай в том же духе! 🚀

---

**Ревьюер:** GitHub Copilot  
**Стиль:** Профессиональный, детальный
