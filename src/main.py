from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from . import models, database, config
from .routers import notes
from .routers import frontend

# TODO: Удалите эту строку! Используйте только Alembic миграции
# При каждом запуске пересоздаются таблицы
# См. REVIEW.md секция "Критические проблемы" пункт 1
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title=config.APP_NAME)

app.include_router(notes.router)

app.include_router(frontend.router)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/", tags=["root"])
def root():
    return {"message": "Open /notes to use the web UI or /api for JSON API"}