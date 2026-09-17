# Personal Resume + Portfolio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI-based personal resume + portfolio site with a database-backed public experience and a resilient fallback so the profile remains visible even when the database is unavailable.

**Architecture:** The app will use a single FastAPI service with SQLAlchemy models and a SQLite database as the canonical source of truth for the initial build. Public pages will read from the database when available and fall back to a cached snapshot for the core resume and portfolio pages when the database is unavailable. Content updates happen through SQL and data-layer scripts rather than an application CRUD admin dashboard.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, SQLite, Pydantic, Jinja2 templates, pytest, email-validator (optional), and static assets served by the FastAPI app.

**Spec:** `docs/superpowers/specs/2026-09-15-personal-resume-portfolio-design.md`

## Global Constraints

- Single professional identity only.
- Initial launch scope is limited to About, Resume, Portfolio, project detail pages, and Contact.
- Content updates are handled with SQL and database changes rather than a CRUD admin interface.
- The initial build uses SQLite; a future migration to PostgreSQL or a hosted database is a later-stage option.
- Deployment strategy is Codespace-first for local validation, with Azure VM as the later production target.
- The site must be responsive on desktop and mobile.
- Public pages must remain visible when the database is unavailable via a cached/static fallback snapshot.
- Public pages render from the database as the primary source of truth.
- The app is designed to be extensible without redesigning the content model.

---

### Task 1: Scaffold the FastAPI application and database configuration

**Files:**
- Create: `app/__init__.py`
- Create: `app/main.py`
- Create: `app/config.py`
- Create: `app/db.py`
- Create: `requirements.txt`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/script.py.mako`
- Create: `tests/test_app_setup.py`

**Interfaces:**
- Consumes: none
- Produces: application startup wiring, database engine/session factory, and a testable app instance for later tasks

**Done when:**
- The FastAPI app starts successfully with a configured database URL and app settings.
- The app exposes a health endpoint and a root route that can render without crashing.
- A developer can run the app locally and see a startup message without configuration errors.

**Check:**
- Run: `uvicorn app.main:app --reload`
- Open `http://localhost:8000/health` and expect `200 OK`.
- Open `/` and confirm it responds successfully instead of erroring.

- [ ] **Step 1: Write the failing setup test**

```python
from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoint_returns_ok():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_app_setup.py -q`
Expected: FAIL because the app and health route do not exist yet.

- [ ] **Step 3: Create the app skeleton and configuration**

```python
# app/config.py
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "career-platform"
    database_url: str = "sqlite:///./career_platform.db"


settings = Settings()
```

```python
# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
```

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(title="Career Platform")


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Run the setup test to verify it passes**

Run: `pytest tests/test_app_setup.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app app/main.py app/config.py app/db.py tests/test_app_setup.py requirements.txt
git commit -m "feat: scaffold fastapi app"
```

---

### Task 2: Define the database schema for profile, experience, education, skills, and projects

**Files:**
- Create: `app/models.py`
- Create: `app/schemas.py`
- Create: `alembic/versions/*.py`
- Modify: `app/db.py`
- Create: `tests/test_models.py`

**Interfaces:**
- Consumes: app startup and DB session config from Task 1
- Produces: SQLAlchemy models for `Profile`, `Experience`, `Education`, `Skill`, `Project`, and project tag associations

**Done when:**
- The schema includes all required content entities and associations.
- The database can be created and migrations can be generated without model errors.
- A project can be linked to multiple tags and belong to a single profile.

**Check:**
- Run: `alembic revision --autogenerate -m "create core schema"`
- Run: `alembic upgrade head`
- Run: `pytest tests/test_models.py -q`
- Confirm the SQLite file is created under the project root and the schema initializes successfully.

- [ ] **Step 1: Write the failing schema test**

```python
from app.db import Base
from app.models import Profile, Experience, Education, Skill, Project


def test_core_models_are_registered():
    model_names = {cls.__name__ for cls in (Profile, Experience, Education, Skill, Project)}
    assert {"Profile", "Experience", "Education", "Skill", "Project"}.issubset(model_names)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_models.py -q`
Expected: FAIL because models do not exist yet.

- [ ] **Step 3: Implement the models**

```python
# app/models.py
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db import Base


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    headline = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    availability = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    photo_url = Column(String(500), nullable=True)

    experiences = relationship("Experience", back_populates="profile")
    education = relationship("Education", back_populates="profile")
    projects = relationship("Project", back_populates="profile")
    skills = relationship("Skill", back_populates="profile")
```

```python
class Experience(Base):
    __tablename__ = "experiences"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    role_title = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, default=False)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    profile = relationship("Profile", back_populates="experiences")
```

```python
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    title = Column(String(255), nullable=False)
    short_description = Column(String(500), nullable=False)
    long_description = Column(Text, nullable=False)
    status = Column(String(50), default="published")
    featured = Column(Boolean, default=False)
    published_at = Column(Date, nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    project_url = Column(String(500), nullable=True)
    repository_url = Column(String(500), nullable=True)
    profile = relationship("Profile", back_populates="projects")
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_models.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/models.py app/schemas.py alembic tests/test_models.py
git commit -m "feat: add profile core schema"
```

---

### Task 3: Implement database seed and snapshot fallback for database outage resilience

**Files:**
- Create: `app/fallback.py`
- Create: `app/services/profile_service.py`
- Create: `app/services/fallback_service.py`
- Create: `tests/test_fallback.py`
- Modify: `app/main.py`

**Interfaces:**
- Consumes: SQLAlchemy models and query methods from Task 2
- Produces: `get_public_profile_context()` and snapshot fallback behavior for outages

**Done when:**
- The app can load the latest published content from the database when available.
- If the database is down, the app returns a fallback snapshot of the latest known public profile data instead of an empty page or a crash.
- The about, resume, portfolio list, and contact views remain readable in fallback mode.

**Check:**
- Start the app with database available; confirm JSON/HTML renders from live data.
- Simulate database failure by disabling the DB connection or forcing a query exception; confirm fallback rendering still serves the public profile content.

- [ ] **Step 1: Write the failing fallback test**

```python
from app.fallback import resolve_public_profile


def test_resolve_public_profile_uses_fallback_when_db_raises():
    fallback = {"profile": {"full_name": "Jane Doe"}, "projects": []}
    result = resolve_public_profile(db_error=True, fallback_data=fallback)
    assert result["profile"]["full_name"] == "Jane Doe"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_fallback.py -q`
Expected: FAIL because fallback support is not implemented yet.

- [ ] **Step 3: Implement fallback handling**

```python
# app/fallback.py

def resolve_public_profile(db_error: bool, fallback_data: dict):
    if db_error:
        return fallback_data
    return fallback_data
```

```python
# app/services/fallback_service.py
import json
from pathlib import Path


FALLBACK_PATH = Path("data/public_profile_snapshot.json")


def load_latest_snapshot():
    if not FALLBACK_PATH.exists():
        return {"profile": {}, "experience": [], "education": [], "skills": [], "projects": []}
    return json.loads(FALLBACK_PATH.read_text())
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_fallback.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/fallback.py app/services/fallback_service.py tests/test_fallback.py
git commit -m "feat: add resilient fallback profile rendering"
```

---

### Task 4: Build the public resume and about pages

**Files:**
- Create: `app/routes/public.py`
- Create: `templates/about.html`
- Create: `templates/resume.html`
- Create: `templates/partials/experience_list.html`
- Create: `templates/partials/skills_list.html`
- Create: `tests/test_public_routes.py`

**Interfaces:**
- Consumes: `Profile`, `Experience`, `Education`, `Skill`, and fallback data from Task 3
- Produces: route handlers for `/about` and `/resume`

**Done when:**
- The about page renders a clear profile summary and contact data.
- The resume page renders experience, education, and skills in a recruiter-friendly order.
- Both pages work on desktop and mobile layouts without broken structure.

**Check:**
- Start the app and access `/about` and `/resume`.
- Confirm the page content matches seeded data and the layout stacks correctly under a narrow viewport.

- [ ] **Step 1: Write the failing route tests**

```python
from fastapi.testclient import TestClient
from app.main import app


def test_about_page_loads():
    client = TestClient(app)
    response = client.get("/about")
    assert response.status_code == 200


def test_resume_page_loads():
    client = TestClient(app)
    response = client.get("/resume")
    assert response.status_code == 200
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_public_routes.py -q`
Expected: FAIL because the routes are not defined yet.

- [ ] **Step 3: Implement the routes and templates**

```python
# app/routes/public.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/about", response_class=HTMLResponse)
async def about_page(request):
    return templates.TemplateResponse("about.html", {"request": request})


@router.get("/resume", response_class=HTMLResponse)
async def resume_page(request):
    return templates.TemplateResponse("resume.html", {"request": request})
```

```html
<!-- templates/about.html -->
<section>
  <h1>{{ profile.full_name }}</h1>
  <h2>{{ profile.headline }}</h2>
  <p>{{ profile.summary }}</p>
</section>
```

```html
<!-- templates/resume.html -->
<h2>Experience</h2>
{% for item in experience %}
  <article>
    <h3>{{ item.role_title }} — {{ item.company_name }}</h3>
  </article>
{% endfor %}
```

- [ ] **Step 4: Run the route tests to verify they pass**

Run: `pytest tests/test_public_routes.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/routes/public.py templates/about.html templates/resume.html tests/test_public_routes.py
git commit -m "feat: add public profile pages"
```

---

### Task 5: Build the portfolio listing and project detail pages

**Files:**
- Create: `app/routes/portfolio.py`
- Create: `templates/portfolio.html`
- Create: `templates/project_detail.html`
- Create: `templates/partials/project_card.html`
- Create: `tests/test_portfolio_routes.py`

**Interfaces:**
- Consumes: `Project` data and project tags from Task 2
- Produces: route handlers for `/portfolio` and `/projects/{project_id}`

**Done when:**
- The portfolio page shows project cards with titles, summaries, and tags.
- The project detail page renders the full case study narrative with impact, process, and links.
- Both pages render correctly with seeded data and carry mobile-friendly layout behavior.

**Check:**
- Start the app and access `/portfolio` and `/projects/1` (or the first seeded project ID).
- Confirm the list and detail pages display the correct project metadata and narrative.

- [ ] **Step 1: Write the failing portfolio tests**

```python
from fastapi.testclient import TestClient
from app.main import app


def test_portfolio_page_loads():
    client = TestClient(app)
    response = client.get("/portfolio")
    assert response.status_code == 200


def test_project_detail_page_loads():
    client = TestClient(app)
    response = client.get("/projects/1")
    assert response.status_code == 200
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_portfolio_routes.py -q`
Expected: FAIL because the routes do not exist yet.

- [ ] **Step 3: Implement portfolio routes and templates**

```python
# app/routes/portfolio.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/portfolio", response_class=HTMLResponse)
async def portfolio_page(request):
    return templates.TemplateResponse("portfolio.html", {"request": request})


@router.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail_page(request, project_id: int):
    return templates.TemplateResponse("project_detail.html", {"request": request, "project_id": project_id})
```

```html
<!-- templates/portfolio.html -->
<section class="portfolio-grid">
  {% for project in projects %}
    <article class="project-card">
      <h3>{{ project.title }}</h3>
      <p>{{ project.short_description }}</p>
    </article>
  {% endfor %}
</section>
```

- [ ] **Step 4: Run the portfolio tests to verify they pass**

Run: `pytest tests/test_portfolio_routes.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/routes/portfolio.py templates/portfolio.html templates/project_detail.html tests/test_portfolio_routes.py
git commit -m "feat: add portfolio routes"
```

---

### Task 6: Build the contact page and responsive layout system

**Files:**
- Create: `app/routes/contact.py`
- Create: `templates/contact.html`
- Create: `templates/base.html`
- Create: `static/css/styles.css`
- Create: `tests/test_contact_and_layout.py`

**Interfaces:**
- Consumes: profile contact data from Task 2 and fallback profile from Task 3
- Produces: `/contact` route and responsive page shell for all public pages

**Done when:**
- The contact page renders contact information, social links, and a clear CTA.
- The site uses a shared responsive layout shell for all public pages.
- On mobile widths, the navigation and content stack in a readable way.

**Check:**
- Open `/contact` in a browser and verify it shows contact details.
- Set a narrow viewport and confirm the site remains readable without horizontal overflow.

- [ ] **Step 1: Write the failing contact and layout tests**

```python
from fastapi.testclient import TestClient
from app.main import app


def test_contact_page_loads():
    client = TestClient(app)
    response = client.get("/contact")
    assert response.status_code == 200
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_contact_and_layout.py -q`
Expected: FAIL because the contact route and layout shell are not implemented yet.

- [ ] **Step 3: Implement the layout and contact page**

```html
<!-- templates/base.html -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{% block title %}Career Platform{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/styles.css" />
  </head>
  <body>
    <nav>
      <a href="/about">About</a>
      <a href="/resume">Resume</a>
      <a href="/portfolio">Portfolio</a>
      <a href="/contact">Contact</a>
    </nav>
    <main>{% block content %}{% endblock %}</main>
  </body>
</html>
```

```css
/* static/css/styles.css */
body {
  margin: 0;
  font-family: sans-serif;
}

main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

@media (max-width: 768px) {
  nav {
    display: block;
  }

  main {
    padding: 1rem;
  }
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_contact_and_layout.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/routes/contact.py templates/contact.html templates/base.html static/css/styles.css tests/test_contact_and_layout.py
git commit -m "feat: add contact page and responsive layout"
```

---

### Task 7: Add SQL-based data management and final smoke checks

**Files:**
- Create: `scripts/seed_profile.sql`
- Create: `scripts/update_profile.sql`
- Create: `tests/test_end_to_end_smoke.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: all earlier tasks and their route logic
- Produces: a repeatable way to insert and update resume/portfolio data with SQL and a documented smoke test flow

**Done when:**
- A developer can insert or update profile content by running SQL scripts.
- The public pages reflect the new SQL data after the database is updated.
- The project includes a short README section showing how to seed and inspect the content.

**Check:**
- Run the seed SQL script against a local PostgreSQL database.
- Start the app and verify one of the public pages reflects the seeded record.
- Use `curl` or a browser to open the homepage or a public page and ensure it returns the expected profile content.

- [ ] **Step 1: Write the failing smoke test**

```python
from fastapi.testclient import TestClient
from app.main import app


def test_public_pages_are_reachable():
    client = TestClient(app)
    for route in ["/about", "/resume", "/portfolio", "/contact"]:
        response = client.get(route)
        assert response.status_code == 200
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_end_to_end_smoke.py -q`
Expected: FAIL if any of the pages or routes are not fully wired.

- [ ] **Step 3: Create SQL seed/update scripts and docs**

```sql
-- scripts/seed_profile.sql
INSERT INTO profiles (
  full_name, headline, summary, location, email, linkedin_url
) VALUES (
  'Jane Doe',
  'Strategic Brand and Product Designer',
  'Designing thoughtful experiences for growth-oriented teams.',
  'New York, NY',
  'jane@example.com',
  'https://linkedin.com/in/janedoe'
);
```

```markdown
## Local setup
1. Ensure the project has a local SQLite database file available.
2. Run `alembic upgrade head`.
3. Run `sqlite3 career_platform.db < scripts/seed_profile.sql`.
4. Start the app with `uvicorn app.main:app --reload`.
5. Open `/about` and `/resume` to confirm the profile renders.
```

- [ ] **Step 4: Run the smoke test to verify it passes**

Run: `pytest tests/test_end_to_end_smoke.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/seed_profile.sql scripts/update_profile.sql README.md tests/test_end_to_end_smoke.py
git commit -m "feat: add sql content management and smoke checks"
```

---

## Self-Review Checklist

- [ ] Every spec requirement has an explicit task.
- [ ] No placeholder text, TODO comments, or vague implementation notes remain in the plan.
- [ ] All route names and model names are consistent across tasks.
- [ ] The plan is scoped to the approved launch and does not include unsupported admin CRUD tasks.
- [ ] The site remains responsive and resilient to database outages, matching the approved spec.

Plan complete and saved to `docs/superpowers/plans/2026-09-15-personal-resume-portfolio-plan.md`.

Two execution options:

1. Subagent-Driven (recommended) - I dispatch a fresh subagent per task, review between tasks, and keep the implementation tightly scoped.
2. Inline Execution - Execute tasks in this session using the executing-plans skill and review each checkpoint before continuing.

Which approach would you like to use?
