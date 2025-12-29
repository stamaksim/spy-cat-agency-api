# Spy Cat Agency API

REST API for managing spy cats, missions, and targets (test assignment).

## Tech Stack
- FastAPI
- SQLModel (SQLite)
- httpx (TheCatAPI integration for breed validation)
- uv (dependency management)
- pytest + FastAPI TestClient
- ruff (lint + formatter)

## Requirements
- Python 3.12+
- `uv` installed

## Setup

Install dependencies:

```bash
uv sync
```

## Run the API locally:
```bash
  uv run uvicorn app.main:app --reload
```

### Useful links
* Swagger UI: http://127.0.0.1:8000/docs
* OpenAPI: http://127.0.0.1:8000/openapi.json
* Healthcheck: http://127.0.0.1:8000/health

#### SQLite database file is created automatically (default: sca.db).

Configuration (optional)  
Create a .env file in the project root if you want to use a TheCatAPI key:  
* DATABASE_URL=sqlite:///./sca.db  
* THECATAPI_KEY=your_key_here  
* BREED_CACHE_TTL_SECONDS=3600

#### Run Tests
```bash
  uv run pytest
```
## API Overview
Spy Cats  
* POST /cats — create a cat (breed validated via TheCatAPI)
* GET /cats — list cats 
* GET /cats/{cat_id} — get a single cat 
* PATCH /cats/{cat_id} — update cat salary 
* DELETE /cats/{cat_id} — delete a cat

Missions / Targets
* POST /missions — create a mission with 1–3 targets in a single request 
* GET /missions — list missions 
* GET /missions/{mission_id} — get a mission (including targets)
* POST /missions/{mission_id}/assign/{cat_id} — assign a cat to a mission
(a cat can have only one active mission at a time)
* PATCH /missions/{mission_id}/targets/{target_id} — update target notes and/or mark target complete
Notes cannot be updated if the target or mission is completed. 
* DELETE /missions/{mission_id} — delete a mission (only if it is not assigned)

## Business Rules Implemented
* A mission has 1..3 targets. 
* Targets must be unique within a mission (name + country). 
* A cat can have only one active mission at a time. 
* Target notes are frozen when the target is complete or the mission is complete. 
* When all targets are complete, the mission is automatically marked as complete. 
* A mission cannot be deleted if it is assigned to a cat.

## Postman Collection
This repository includes a Postman collection and an example local environment:

- `postman/Spy Cat Agency API.postman_collection.json`
- `postman/Local.postman_environment.json`

### How to use
1. Start the API:
```bash
  uv run uvicorn app.main:app --reload
```
2. In Postman:

* Import the collection: postman/Spy Cat Agency API.postman_collection.json 
* Import the environment: postman/Local.postman_environment.json 
* Select environment Local (top-right). 
* Ensure the environment variable base_url is set to: http://127.0.0.1:8000