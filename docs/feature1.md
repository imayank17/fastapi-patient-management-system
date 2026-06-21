# Feature 1: Modular Project Structure Refactoring

## What Have Been Done

The entire FastAPI Patient Management System was refactored from a **single `main.py` file** into a **well-organized modular package structure**.

### Before (Old Structure)

```
fastapi-demo-api/
├── main.py            # Everything in one file (models, routes, logic, storage)
├── patients.json
└── requirements.txt
```

### After (New Structure)

```
fastapi-demo-api/
├── app/
│   ├── __init__.py           # Makes app a Python package
│   ├── main.py               # App entry point — creates FastAPI app, registers routers
│   ├── database.py           # Data access layer — load_data() and save_data()
│   │
│   ├── models/
│   │   └── __init__.py       # Placeholder for future SQLAlchemy ORM models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── patient.py        # Patient and PatientUpdate Pydantic schemas
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── patient.py        # All patient CRUD routes using APIRouter
│   │
│   └── services/
│       └── __init__.py       # Placeholder for future business logic
│
├── main.py                    # Original file kept as reference
├── patients.json              # JSON storage (unchanged)
└── requirements.txt
```

### Specific Changes

| Change | Details |
|--------|---------|
| **Schemas extracted** | `Patient` and `PatientUpdate` Pydantic models moved to `app/schemas/patient.py` |
| **Routes extracted** | All 6 patient endpoints moved to `app/routers/patient.py` using `APIRouter` |
| **Database layer created** | `load_data()` and `save_data()` moved to `app/database.py` with proper file path handling |
| **Entry point created** | New `app/main.py` — creates the FastAPI app, registers routers, keeps only `/` and `/about` routes |
| **Placeholders added** | `models/` and `services/` directories created for future SQLAlchemy and business logic |
| **Minor fix applied** | Changed deprecated `example=` to `examples=[]` in Path parameter |

### All Endpoints Preserved

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/about` | API description |
| GET | `/view` | Get all patients |
| GET | `/patient/{patient_id}` | Get a specific patient |
| GET | `/sort?sort_by=...&order=...` | Sort patients by height, weight, or BMI |
| POST | `/create` | Create a new patient |
| PUT | `/edit/{patient_id}` | Update an existing patient |
| DELETE | `/delete/{patient_id}` | Delete a patient |

---

## Why Have Been Done

### 1. Single File Doesn't Scale

Having all models, routes, and logic in one `main.py` works for small demos but becomes **hard to read, maintain, and debug** as the project grows. Adding features like authentication, new entities, or a frontend would make the file unmanageable.

### 2. Separation of Concerns

Each layer now has a **single responsibility**:

- **`schemas/`** → Defines *what* the data looks like (validation)
- **`routers/`** → Defines *where* the endpoints are (URL handling)
- **`database.py`** → Defines *how* data is stored (persistence)
- **`models/`** → Will define *how* data maps to the database (ORM)
- **`services/`** → Will hold *business logic* (calculations, rules)

### 3. Future-Proofing

The modular structure makes it easy to:

- **Add JWT authentication** → Just create `app/routers/auth.py` and register it
- **Switch from JSON to SQLite** → Only modify `database.py` and add models in `models/`
- **Add a React frontend** → API structure is clean and ready for CORS integration
- **Add new entities** → Create new schema, router, and model files without touching existing code

### 4. FastAPI Best Practices

Using `APIRouter` for route grouping is the **recommended approach** in the official FastAPI documentation. It enables:

- Route prefixing and tagging
- Independent testing of route groups
- Clean dependency injection per router

---

## How Have Been Done

### Step 1: Created the Package Structure

Created the `app/` directory with `__init__.py` files to make it a proper Python package. Added subdirectories for each layer:

```
app/__init__.py
app/models/__init__.py
app/schemas/__init__.py
app/routers/__init__.py
app/services/__init__.py
```

### Step 2: Extracted Pydantic Schemas (`app/schemas/patient.py`)

Moved the `Patient` and `PatientUpdate` classes from the old `main.py` into their own file. No logic was changed — just the location.

```python
# app/schemas/patient.py
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional

class Patient(BaseModel):
    id: Annotated[str, Field(...)]
    name: Annotated[str, Field(...)]
    # ... all fields preserved exactly
    
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        # ... same logic as before

class PatientUpdate(BaseModel):
    # ... all optional fields preserved
```

### Step 3: Created the Database Layer (`app/database.py`)

Moved `load_data()` and `save_data()` into a dedicated module. Used `os.path` to resolve the JSON file path correctly regardless of where the app is run from.

```python
# app/database.py
import json, os

JSON_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'patients.json')

def load_data():
    with open(JSON_FILE_PATH, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(data, f)
```

### Step 4: Extracted Routes to APIRouter (`app/routers/patient.py`)

Moved all 6 patient endpoints from the old `main.py` into an `APIRouter`. Updated imports to use the new schema and database module paths.

```python
# app/routers/patient.py
from fastapi import APIRouter
from app.schemas.patient import Patient, PatientUpdate
from app.database import load_data, save_data

router = APIRouter()

@router.get('/view')
def view():
    data = load_data()
    return data

# ... all other routes moved here with identical logic
```

### Step 5: Created the New Entry Point (`app/main.py`)

Created a slim `main.py` that only does three things:
1. Creates the FastAPI app with metadata
2. Registers the patient router
3. Keeps the general info endpoints (`/` and `/about`)

```python
# app/main.py
from fastapi import FastAPI
from app.routers import patient as patient_router

app = FastAPI(title="Patient Management System", version="1.0.0")

app.include_router(patient_router.router)

@app.get("/")
def hello():
    return {'message': 'Patient Management System API'}
```

### Step 6: Verified Everything Works

Started the server and tested all endpoints with `curl`:

```bash
# How to run the refactored app
source venv/bin/activate
uvicorn app.main:app --reload
```

All 6 patient endpoints + 2 info endpoints returned the same responses as before. No functionality was broken.

---

## Run Command Change

> **Important:** The run command changed from the old format to the new format:
>
> ```bash
> # Old
> uvicorn main:app --reload
>
> # New
> uvicorn app.main:app --reload
> ```
