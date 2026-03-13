# Copilot Instructions for minigolf-app

## Project Overview

A FastAPI-based web application for tracking miniature golf games. The app allows users to create games, add players, record scores for individual holes, and track game progress.

## Architecture

**Tech Stack:**
- Backend: FastAPI with SQLAlchemy ORM
- Frontend: Jinja2 templates (HTML + HTMX for dynamic interactions)
- Database: SQLite (local file `minigolf.db`)
- Testing: pytest

**Core Structure:**
- `main.py` - FastAPI application entry point and route handlers
- `models.py` - SQLAlchemy ORM models (Game, Player, Score) with relationships
  - Game ↔ Player: many-to-many relationship via `game_players` join table
  - Game ↔ Score: one-to-many (a game has multiple scores)
  - Player ↔ Score: one-to-many (a player can have scores across multiple games)
- `crud.py` - Database operations (create/read for games, players, scores)
- `database.py` - SQLAlchemy engine and session configuration
- `frontend/templates/` - HTML templates for rendering pages and partials

**Key Design Patterns:**
- Dependency injection: `get_db()` dependency provides database session to routes
- Route separation: Game creation (`/start-game`) is separate from score recording (not yet implemented)
- Player reuse: Creating a game checks for existing players before creating new ones
- Template-based responses: Routes return `TemplateResponse` for server-side rendering (HTMX-friendly)

## Build, Test & Development

**Install dependencies:**
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

**Run development server:**
```bash
python main.py
# Server runs on http://0.0.0.0:8000
```

**Run all tests:**
```bash
pytest test_game_logic.py -v
```

**Run a single test:**
```bash
pytest test_game_logic.py::test_create_and_get_player -v
```

**Notes:**
- Tests use an in-memory SQLite database (`:memory:`) for isolation
- Each test function gets a fresh database via the `db` fixture
- Database tables are auto-created from models on app startup (see `models.Base.metadata.create_all()`)

## Key Conventions

**Database Session Management:**
- Always pass `db: Session = Depends(get_db)` to route handlers that need database access
- Session is automatically closed after the request completes

**Player Naming:**
- Player names are unique (defined as `unique=True` in model)
- When creating a game, the CRUD layer reuses existing players by name to avoid duplicates

**Game Model:**
- `number_of_holes` defaults to 18 (standard golf course)
- Score recording happens after game creation
- Scores are tied to both a player and a game (not just a player)

**Testing:**
- Use the `db` pytest fixture for all database-dependent tests
- Tests are organized by functionality (players, games, scores)
- Each test is independent; no test should depend on the state created by another

**Frontend/Template Responses:**
- Routes return `TemplateResponse` objects with `request` and context data
- Partials are rendered from `frontend/templates/partials/` and can be swapped in dynamically
- Template directory is resolved relative to the script location

## Common Tasks

**Adding a new API endpoint:**
1. Define the route in `main.py` with appropriate dependencies
2. Add corresponding CRUD function(s) in `crud.py` if needed
3. Create/update template if returning HTML
4. Add test(s) in `test_game_logic.py`

**Adding a database field to a model:**
1. Update the model in `models.py` with a new `Column`
2. Migration: SQLite doesn't have migrations; manually update existing `minigolf.db` or delete it to regenerate
3. Update any CRUD functions that reference the model
4. Update tests to verify the new field

**Recording scores:**
- Use `crud.record_score(db, game_id, player_id, hole_number, strokes)` to add a score
- Retrieve all scores for a game with `crud.get_game_scores(db, game_id)`
