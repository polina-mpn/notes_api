Notes API — учебный проект на FastAPI

Данный проект представляет собой веб-приложение для управления заметками.
Реализован на FastAPI (синхронный режим) с использованием SQLite, SQLAlchemy и Jinja2.
Проект содержит простой пользовательский интерфейс на HTML/CSS.

---

Основные возможности

1. создание, редактирование, удаление заметок; 
2. просмотр списка всех заметок с кратеой информацией; 
3. просмотр содержимого отдельной заметки;
4. назначение категории, тегов, статуса и уровня важности к каждой заметке; 
5. Установка даты напоминания.

Дополнительно:

1. Категории 
2. Теги
3. Статус заметки
4. Важность
5. Дата напоминания


---

Структура проекта

project/
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── config.py
│   ├── routers/
│   │   ├── notes.py
│   │   └── frontend.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── note_create.html
│   │   ├── note_edit.html
│   │   ├── note_view.html
│   └── static/
│       └── styles.css
│
├── tests
│   ├── __init__.py
│   ├── api_test.py
│   ├── conftest.py
│   └── crud_test.py
│
├── alembic.ini
├── .gitignore
├── requirements.txt
└── README.md


---

Фронтенд

Пользовательский интерфейс построен на:

1. HTML + Jinja2 
2. CSS (src / static / style.css)


Функциональность интерфейса:

1. Просмотр списка заметок в виде карточек

2. Переход к детальному представлению заметки

3. Создание новых заметок через HTML-форму

4. Редактирование существующих заметок

5. Удаление заметки

6. Отображение тегов, категорий, статуса и важности

---
Установка и запуск

1. Клонирование проекта

git clone https://github.com/polina-mpn/notes_api.git

cd PythonProject

2. Создание виртуального окружения

Windows:

python -m venv venv

Linux / macOS:

python3 -m venv .venv

3. Активация виртуального окружения

Windows:

venv\Scripts\activate

Linux / macOS:

source venv/bin/activate

4. Установка зависимостей

pip install -r requirements.txt

5. Запуск приложения

uvicorn src.main:app --reload

После запуска приложение будет доступно по адресу:
http://127.0.0.1:8000/notes


---

Технологии:

1. Python 3.12

2. FastAPI

3. SQLAlchemy

4. SQLite

5. Jinja2

6. Uvicorn



---

Назначение проекта

Проект создан в учебных целях и демонстрирует базовые навыки работы с FastAPI, взаимодействия с базой данных и реализации простого веб-интерфейса.