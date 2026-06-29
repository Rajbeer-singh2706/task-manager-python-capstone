# Full-Stack Task Manager — Project Context

> **Standalone reference for independent development.**
> This document contains everything you need to build the capstone project from scratch — architecture, data models, API spec, folder structure, config files, and day-by-day build plan.

---

## Project Summary

| Detail | Value |
|--------|-------|
| **Project Name** | Full-Stack Task Manager |
| **Total Build Time** | 10 hours across 5 days |
| **Stack** | Python 3.12 · FastAPI · SQLAlchemy · SQLite · Streamlit · Pandas · Pytest · Docker |
| **Goal** | A REST API + Streamlit web UI for task management, with a Pandas analytics layer |

---

## What You Are Building

A full-stack task management application with three layers:

```
┌──────────────────────────┐
│   Streamlit Web UI        │  ← Users interact here (pages for tasks, categories, analytics)
├──────────────────────────┤
│   FastAPI REST API        │  ← All business logic, validation, error handling
├──────────────────────────┤
│   SQLAlchemy + SQLite     │  ← Persistent relational storage
└──────────────────────────┘
```

The Streamlit UI communicates with FastAPI **exclusively via HTTP requests** — it never touches the database directly. The FastAPI layer is also independently usable via Swagger UI at `/docs`.

---

## Technology Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | Language |
| FastAPI | ≥ 0.115.0 | REST API framework |
| Uvicorn | ≥ 0.30.0 | ASGI server for FastAPI |
| SQLAlchemy | ≥ 2.0.0 | ORM — maps Python classes to DB tables |
| SQLite | built-in | File-based relational database |
| Pydantic | ≥ 2.0.0 | Request/response validation |
| Streamlit | ≥ 1.35.0 | Web UI framework |
| Pandas | ≥ 2.2.0 | Analytics layer + CSV export |
| Requests | ≥ 2.31.0 | HTTP client for Streamlit → API calls |
| Pytest | ≥ 8.0.0 | Test framework |
| pytest-cov | ≥ 5.0.0 | Coverage reports |
| httpx | ≥ 0.27.0 | Async HTTP client for tests |
| Docker | latest | Containerisation + deployment |
| uv | latest | Package manager (replaces pip + venv) |

---

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Create a task with title, description, due date, priority, and category | High |
| FR-02 | List all tasks with filtering by status, priority, and category | High |
| FR-03 | Mark a task as complete | High |
| FR-04 | Update task details | High |
| FR-05 | Delete a task | High |
| FR-06 | Create and manage categories | Medium |
| FR-07 | Streamlit dashboard showing task statistics | Medium |
| FR-08 | Analytics: completion rate by category, overdue report | Medium |
| FR-09 | Export tasks to CSV | Low |
| FR-10 | Auto-generated Swagger UI at `/docs` | Low |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | API response time < 200ms for all CRUD operations |
| NFR-02 | 80%+ test coverage (enforced by pytest-cov) |
| NFR-03 | Dockerised — runs with a single `docker run` command |
| NFR-04 | Deployable to Render or Railway (free tier) |
| NFR-05 | Professional README with setup instructions and API screenshots |

---

## Database Design (ERD)

### Tables

#### `categories`
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| name | TEXT | NOT NULL, UNIQUE |
| color | TEXT | DEFAULT `'#3B82F6'` |
| created_at | DATETIME | DEFAULT `now()` |

#### `tasks`
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| title | TEXT | NOT NULL |
| description | TEXT | NULLABLE |
| due_date | DATE | NULLABLE |
| priority | TEXT | CHECK `low` / `medium` / `high`, DEFAULT `medium` |
| status | TEXT | CHECK `pending` / `done`, DEFAULT `pending` |
| category_id | INTEGER | FOREIGN KEY → `categories.id`, NULLABLE |
| created_at | DATETIME | DEFAULT `now()` |
| updated_at | DATETIME | DEFAULT `now()`, auto-update on change |

### Relationship
- **One Category → Many Tasks** (many-to-one from tasks side)
- `tasks.category_id` is nullable — a task can exist without a category

---

## Folder Structure

```
task_manager/
├── app/                            # FastAPI application package
│   ├── __init__.py
│   ├── main.py                     # FastAPI app creation, router registration, lifespan
│   ├── database.py                 # Engine, SessionLocal, Base, get_db dependency
│   ├── models.py                   # SQLAlchemy ORM models (Task, Category)
│   ├── schemas.py                  # Pydantic schemas (request + response)
│   ├── crud.py                     # All database CRUD functions
│   └── routers/
│       ├── __init__.py
│       ├── tasks.py                # /tasks endpoints
│       └── categories.py          # /categories endpoints
│
├── streamlit_app/                  # Streamlit web UI package
│   ├── __init__.py
│   ├── app.py                      # Streamlit entry point (home/landing page)
│   ├── utils.py                    # API client helpers (get, post, put, delete wrappers)
│   └── pages/
│       ├── 01_Dashboard.py         # Overview: stats cards, charts
│       ├── 02_Tasks.py             # Create, list, filter, complete, delete tasks
│       ├── 03_Categories.py        # Create and manage categories
│       └── 04_Analytics.py         # Pandas analytics + CSV export
│
├── analytics/                      # Pandas analytics module
│   ├── __init__.py
│   └── reports.py                  # completion_rate(), overdue_report(), export_csv()
│
├── tests/                          # pytest test suite
│   ├── __init__.py
│   ├── conftest.py                 # fixtures: test DB engine, TestClient
│   ├── test_tasks.py               # task endpoint tests (CRUD)
│   └── test_categories.py          # category endpoint tests
│
├── pyproject.toml                  # project metadata + dependencies
├── Dockerfile                      # container build instructions
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Key File Contents

### `app/database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `app/models.py`
```python
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String, default="#3B82F6")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="category")

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String, default="medium")   # low/medium/high
    status: Mapped[str] = mapped_column(String, default="pending")    # pending/done
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    category: Mapped[Optional[Category]] = relationship("Category", back_populates="tasks")
```

### `app/schemas.py`
```python
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field

# ── Category ──────────────────────────────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#3B82F6")

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    created_at: datetime
    model_config = {"from_attributes": True}

# ── Task ──────────────────────────────────────────────────────────────────────
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    status: str = Field(default="pending", pattern="^(pending|done)$")
    category_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    status: Optional[str] = Field(None, pattern="^(pending|done)$")
    category_id: Optional[int] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    due_date: Optional[date]
    priority: str
    status: str
    category_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
```

### `app/crud.py`
```python
from sqlalchemy.orm import Session
from app import models, schemas

# ── Category CRUD ─────────────────────────────────────────────────────────────
def get_categories(db: Session) -> list[models.Category]:
    return db.query(models.Category).all()

def get_category(db: Session, category_id: int) -> models.Category | None:
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def create_category(db: Session, data: schemas.CategoryCreate) -> models.Category:
    obj = models.Category(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def update_category(db: Session, category_id: int, data: schemas.CategoryUpdate) -> models.Category | None:
    obj = get_category(db, category_id)
    if not obj: return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

def delete_category(db: Session, category_id: int) -> bool:
    obj = get_category(db, category_id)
    if not obj: return False
    db.delete(obj); db.commit()
    return True

# ── Task CRUD ─────────────────────────────────────────────────────────────────
def get_tasks(db: Session, status: str | None = None,
              priority: str | None = None, category_id: int | None = None) -> list[models.Task]:
    q = db.query(models.Task)
    if status:      q = q.filter(models.Task.status == status)
    if priority:    q = q.filter(models.Task.priority == priority)
    if category_id: q = q.filter(models.Task.category_id == category_id)
    return q.all()

def get_task(db: Session, task_id: int) -> models.Task | None:
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_task(db: Session, data: schemas.TaskCreate) -> models.Task:
    obj = models.Task(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def update_task(db: Session, task_id: int, data: schemas.TaskUpdate) -> models.Task | None:
    obj = get_task(db, task_id)
    if not obj: return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

def delete_task(db: Session, task_id: int) -> bool:
    obj = get_task(db, task_id)
    if not obj: return False
    db.delete(obj); db.commit()
    return True
```

### `app/main.py`
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import tasks, categories

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)   # create tables on startup
    yield

app = FastAPI(
    title="Task Manager API",
    description="Full-Stack Task Manager — FastAPI + Streamlit",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(tasks.router,      prefix="/tasks",      tags=["Tasks"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Task Manager API is running"}
```

### `app/routers/tasks.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from typing import Optional

router = APIRouter()

@router.get("/", response_model=list[schemas.TaskResponse])
def list_tasks(status: Optional[str] = None, priority: Optional[str] = None,
               category_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_tasks(db, status=status, priority=priority, category_id=category_id)

@router.post("/", response_model=schemas.TaskResponse, status_code=201)
def create_task(data: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, data)

@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, data: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = crud.update_task(db, task_id, data)
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}/complete", response_model=schemas.TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.update_task(db, task_id, schemas.TaskUpdate(status="done"))
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    if not crud.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
```

### `app/routers/categories.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=list[schemas.CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

@router.post("/", response_model=schemas.CategoryResponse, status_code=201)
def create_category(data: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, data)

@router.get("/{category_id}", response_model=schemas.CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = crud.get_category(db, category_id)
    if not cat: raise HTTPException(status_code=404, detail="Category not found")
    return cat

@router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(category_id: int, data: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    cat = crud.update_category(db, category_id, data)
    if not cat: raise HTTPException(status_code=404, detail="Category not found")
    return cat

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    if not crud.delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
```

### `analytics/reports.py`
```python
import pandas as pd
from datetime import date

def completion_rate(tasks: list[dict]) -> dict:
    """Returns overall and per-category completion rates."""
    df = pd.DataFrame(tasks)
    if df.empty:
        return {"overall": 0.0, "by_category": {}}
    overall = round((df["status"] == "done").mean() * 100, 1)
    by_cat = (
        df.groupby("category_id")["status"]
        .apply(lambda s: round((s == "done").mean() * 100, 1))
        .to_dict()
    )
    return {"overall": overall, "by_category": by_cat}

def overdue_report(tasks: list[dict]) -> list[dict]:
    """Returns pending tasks whose due_date is before today."""
    df = pd.DataFrame(tasks)
    if df.empty or "due_date" not in df.columns:
        return []
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
    today = pd.Timestamp(date.today())
    overdue = df[(df["status"] == "pending") & (df["due_date"] < today)].copy()
    overdue["days_overdue"] = (today - overdue["due_date"]).dt.days
    return overdue.to_dict(orient="records")

def export_csv(tasks: list[dict], path: str) -> str:
    """Exports task list to CSV. Returns the path written."""
    df = pd.DataFrame(tasks)
    df.to_csv(path, index=False)
    return path
```

### `streamlit_app/utils.py`
```python
import requests

API_BASE = "http://localhost:8000"

def get(endpoint: str, params: dict = None) -> list | dict | None:
    try:
        r = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return None

def post(endpoint: str, data: dict) -> dict | None:
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None

def put(endpoint: str, data: dict) -> dict | None:
    try:
        r = requests.put(f"{API_BASE}{endpoint}", json=data, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None

def patch(endpoint: str) -> dict | None:
    try:
        r = requests.patch(f"{API_BASE}{endpoint}", timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None

def delete(endpoint: str) -> bool:
    try:
        r = requests.delete(f"{API_BASE}{endpoint}", timeout=5)
        return r.status_code == 204
    except requests.RequestException:
        return False
```

### `tests/conftest.py`
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_engine):
    TestSessionLocal = sessionmaker(bind=db_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

### `pyproject.toml`
```toml
[project]
name = "task-manager"
version = "0.1.0"
description = "Full-Stack Task Manager — FastAPI + Streamlit"
requires-python = ">=3.12"

dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "streamlit>=1.35.0",
    "pandas>=2.2.0",
    "requests>=2.31.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "httpx>=0.27.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=app --cov-report=term-missing"
```

### `Dockerfile`
```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv sync --no-dev

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `.gitignore`
```
__pycache__/
*.py[cod]
.venv/
*.db
*.sqlite3
.env
.env.*
.coverage
htmlcov/
.pytest_cache/
dist/
*.egg-info/
.mypy_cache/
.dockerignore
```

---

## API Endpoints

### Tasks — `/tasks`

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/tasks/` | List all tasks (supports `?status=`, `?priority=`, `?category_id=` filters) | — | `List[TaskResponse]` |
| POST | `/tasks/` | Create a task | `TaskCreate` | `TaskResponse` (201) |
| GET | `/tasks/{id}` | Get single task | — | `TaskResponse` |
| PUT | `/tasks/{id}` | Update task | `TaskUpdate` | `TaskResponse` |
| PATCH | `/tasks/{id}/complete` | Mark task done | — | `TaskResponse` |
| DELETE | `/tasks/{id}` | Delete task | — | 204 No Content |

### Categories — `/categories`

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/categories/` | List all categories | — | `List[CategoryResponse]` |
| POST | `/categories/` | Create category | `CategoryCreate` | `CategoryResponse` (201) |
| GET | `/categories/{id}` | Get single category | — | `CategoryResponse` |
| PUT | `/categories/{id}` | Update category | `CategoryUpdate` | `CategoryResponse` |
| DELETE | `/categories/{id}` | Delete category | — | 204 No Content |

### Error Responses
- `404 Not Found` — resource does not exist
- `422 Unprocessable Entity` — Pydantic validation failed (auto-generated by FastAPI)

---

## Streamlit Pages

### `streamlit_app/app.py` — Home / Landing
- App title and description
- Links to all pages in the sidebar
- Health check — pings `GET /` and shows API status

### `pages/01_Dashboard.py` — Overview Dashboard
- Stats cards: total tasks, completed, pending, overdue count
- Bar chart: tasks by priority
- Pie chart: completion breakdown
- Table: recent tasks

### `pages/02_Tasks.py` — Task Management
- Filter bar: status / priority / category dropdowns
- Task table with all fields
- "Add Task" form: title, description, due date, priority, category selector
- Per-row buttons: ✅ Complete · 🗑 Delete

### `pages/03_Categories.py` — Category Management
- List all categories with task counts
- "Add Category" form: name + color picker
- Edit / delete per row

### `pages/04_Analytics.py` — Analytics & Export
- Completion rate overall + per category (uses `analytics/reports.py`)
- Overdue tasks table with days-overdue column
- "Export to CSV" button — downloads via `st.download_button`

---

## Streamlit ↔ API Data Flow

```
User fills form in Streamlit
        ↓
utils.post("/tasks/", data) → HTTP POST → FastAPI
        ↓
FastAPI validates with Pydantic schema
        ↓
crud.create_task(db, data) → SQLAlchemy → SQLite
        ↓
Returns TaskResponse JSON
        ↓
Streamlit re-renders with updated data
```

---

## Day-by-Day Build Plan

### Day 26 — Planning & Architecture ✅ (covered in session)
- Requirements spec, ERD, folder scaffold
- uv environment + pyproject.toml
- Git init + .gitignore + first commit
- **Deliverable:** Clean project scaffold committed to Git

### Day 27 — Core Backend
Build order (do it in this exact sequence):
1. `app/database.py` — engine, session, Base, get_db
2. `app/models.py` — Task and Category ORM models
3. `app/schemas.py` — all Pydantic schemas
4. `app/crud.py` — all CRUD functions
5. `app/routers/categories.py` — category endpoints
6. `app/routers/tasks.py` — task endpoints
7. `app/main.py` — app factory, router registration, lifespan
8. Run `uvicorn app.main:app --reload` and test at `http://localhost:8000/docs`

- **Deliverable:** Working REST API, all endpoints testable via Swagger UI

### Day 28 — Streamlit UI & Data Layer
Build order:
1. `streamlit_app/utils.py` — API client helper functions
2. `analytics/reports.py` — completion_rate, overdue_report, export_csv
3. `streamlit_app/app.py` — home page + API health check
4. `pages/01_Dashboard.py` — stats cards and charts
5. `pages/02_Tasks.py` — full task CRUD UI
6. `pages/03_Categories.py` — category management UI
7. `pages/04_Analytics.py` — analytics + CSV export
8. Run `streamlit run streamlit_app/app.py` alongside the API

- **Deliverable:** Fully functional Streamlit UI connected to the FastAPI backend

### Day 29 — Testing & Refinement
Build order:
1. `tests/conftest.py` — in-memory SQLite fixtures + TestClient
2. `tests/test_categories.py` — CRUD tests for all category endpoints
3. `tests/test_tasks.py` — CRUD tests for all task endpoints + filters + complete endpoint
4. Run `pytest --cov=app --cov-report=term-missing` — aim for 80%+
5. Code review pass — clean up, add docstrings, remove debug prints

- **Deliverable:** Full test suite with 80%+ coverage, clean codebase

### Day 30 — Deploy & Portfolio
Build order:
1. Write `Dockerfile` and `.dockerignore`
2. `docker build -t task-manager .` and `docker run -p 8000:8000 task-manager`
3. Push to GitHub — create repo, push main branch
4. Deploy to Render (connect GitHub repo → Web Service → `uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
5. Write `README.md` — badges, screenshots, setup instructions, API docs
6. Optional: record a 2-minute demo video

- **Deliverable:** Live deployed app + polished GitHub portfolio repository

---

## Setup Commands (Quick Reference)

```bash
# 1. Create and enter project directory
mkdir task_manager && cd task_manager

# 2. Initialise uv project
uv init --no-workspace
uv venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows

# 3. Install all dependencies
uv add fastapi "uvicorn[standard]" sqlalchemy pydantic streamlit pandas requests
uv add --dev pytest pytest-cov httpx

# 4. Run the API
uvicorn app.main:app --reload
# Open: http://localhost:8000/docs

# 5. Run Streamlit (separate terminal, venv activated)
streamlit run streamlit_app/app.py
# Opens: http://localhost:8501

# 6. Run tests
pytest

# 7. Build Docker image
docker build -t task-manager .
docker run -p 8000:8000 task-manager
```

---

## Testing Cheatsheet

```python
# tests/test_tasks.py — example patterns

def test_create_task(client):
    r = client.post("/tasks/", json={"title": "Test task", "priority": "high"})
    assert r.status_code == 201
    assert r.json()["title"] == "Test task"

def test_get_task_not_found(client):
    r = client.get("/tasks/999")
    assert r.status_code == 404

def test_complete_task(client):
    task = client.post("/tasks/", json={"title": "My task"}).json()
    r = client.patch(f"/tasks/{task['id']}/complete")
    assert r.status_code == 200
    assert r.json()["status"] == "done"

def test_filter_by_status(client):
    client.post("/tasks/", json={"title": "Done task", "status": "done"})
    client.post("/tasks/", json={"title": "Pending task"})
    r = client.get("/tasks/?status=done")
    assert all(t["status"] == "done" for t in r.json())
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'app'` | Running from wrong directory | Run `uvicorn` from the `task_manager/` root |
| `sqlalchemy.exc.OperationalError: no such table` | Tables not created | Check `Base.metadata.create_all(bind=engine)` runs on startup |
| `422 Unprocessable Entity` | Invalid request body | Check Pydantic schema field names and types |
| `ConnectionRefusedError` in Streamlit | API not running | Start FastAPI with `uvicorn app.main:app --reload` first |
| `ImportError` in tests | Missing `__init__.py` | Add empty `__init__.py` to `tests/` and `app/` |
| `sqlite3.OperationalError: database is locked` | Multiple processes writing | Use `check_same_thread=False` in `create_engine` |
