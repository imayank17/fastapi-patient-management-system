# Feature 2: SQLite Database Migration with SQLAlchemy

## What Have Been Done

Replaced the temporary `patients.json` file-based storage with a proper **SQLite database** using **SQLAlchemy ORM**. The application now persists patient data in `patients.db` with full relational database capabilities.

### Files Changed

| Action | File | What Changed |
|--------|------|-------------|
| **NEW** | `app/models/patient.py` | SQLAlchemy `Patient` model with auto BMI/verdict calculation |
| **MODIFIED** | `app/database.py` | Replaced JSON load/save with SQLAlchemy engine, session, and dependency |
| **MODIFIED** | `app/schemas/patient.py` | Split into `PatientCreate`, `PatientUpdate`, `PatientResponse` |
| **MODIFIED** | `app/routers/patient.py` | Replaced all JSON operations with database queries |
| **MODIFIED** | `app/main.py` | Added automatic table creation on startup |
| **MODIFIED** | `requirements.txt` | Added `sqlalchemy` |

### Updated Folder Structure

```
fastapi-demo-api/
├── app/
│   ├── __init__.py
│   ├── main.py               # Now creates DB tables on startup
│   ├── database.py            # SQLAlchemy engine, session, get_db dependency
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── patient.py         # [NEW] SQLAlchemy Patient model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── patient.py         # Updated: PatientCreate, PatientUpdate, PatientResponse
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── patient.py         # Updated: uses DB sessions instead of JSON
│   │
│   └── services/
│       └── __init__.py
│
├── patients.db                 # [NEW] SQLite database file (auto-created)
├── patients.json               # Old storage (no longer used)
├── requirements.txt            # Added sqlalchemy
└── main.py                     # Original file (kept as reference)
```

### All Endpoints Preserved

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/` | Welcome message | ✅ |
| GET | `/about` | API description | ✅ |
| GET | `/view` | Get all patients | ✅ |
| GET | `/patient/{patient_id}` | Get a specific patient | ✅ |
| GET | `/sort?sort_by=...&order=...` | Sort patients | ✅ |
| POST | `/create` | Create a new patient | ✅ |
| PUT | `/edit/{patient_id}` | Update a patient | ✅ |
| DELETE | `/delete/{patient_id}` | Delete a patient | ✅ |

### Bug Fix Included

The BMI verdict logic had an error in the original code — the 25–30 BMI range was returning `"Normal"` instead of `"Overweight"`. This has been corrected:

```python
# Before (incorrect)
elif self.bmi < 30:
    return 'Normal'      # ❌ Should be Overweight

# After (fixed)
elif bmi < 30:
    return 'Overweight'  # ✅ Correct
```

---

## Why Have Been Done

### 1. JSON Storage Is Not Production-Ready

Storing data in a JSON file has several critical problems:

- **No concurrency support** — Multiple simultaneous requests can corrupt the file
- **No data integrity** — No constraints, no types, no relationships
- **Poor performance** — Every request reads/writes the entire file
- **No querying power** — Sorting and filtering must be done in Python code

### 2. SQLite + SQLAlchemy Provides Real Database Features

- **ACID transactions** — Data is safe even during crashes
- **Concurrent reads** — Multiple users can read simultaneously
- **Indexed lookups** — Fast `O(log n)` lookups by patient ID
- **SQL sorting** — Sorting is done by the database engine, not Python
- **Schema enforcement** — Column types and constraints are enforced at the DB level

### 3. SQLAlchemy ORM Keeps Code Pythonic

Instead of writing raw SQL queries, SQLAlchemy lets us work with Python objects:

```python
# Instead of: SELECT * FROM patients WHERE id = 'P001'
patient = db.query(Patient).filter(Patient.id == "P001").first()

# Instead of: INSERT INTO patients VALUES (...)
db.add(new_patient)
db.commit()
```

### 4. Dependency Injection Follows FastAPI Best Practices

Using `Depends(get_db)` for session management:
- Automatically creates a session for each request
- Automatically closes the session after the response
- Makes routes easy to test by swapping the dependency

### 5. Easy to Scale Later

SQLite works great for development. When moving to production, changing to PostgreSQL or MySQL only requires changing the `DATABASE_URL` in `database.py` — no other code changes needed.

---

## How Have Been Done

### Step 1: Set Up SQLAlchemy (`app/database.py`)

Replaced the JSON `load_data()`/`save_data()` functions with SQLAlchemy configuration:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file
DATABASE_URL = "sqlite:///./patients.db"

# Engine — manages the connection to the database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory — creates new sessions for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class — all models inherit from this
Base = declarative_base()

# Dependency — injects a DB session into route handlers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Key decisions:**
- `check_same_thread=False` is required because SQLite doesn't allow multi-threaded access by default, but FastAPI is multi-threaded
- `yield` in `get_db()` ensures the session is always closed, even if the route throws an error

### Step 2: Create the Patient Model (`app/models/patient.py`)

Defined the SQLAlchemy ORM model with all 9 columns matching the original data structure:

```python
class Patient(Base):
    __tablename__ = 'patients'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)        # auto-calculated
    verdict = Column(String, nullable=False)    # auto-calculated
```

**Auto-calculation via SQLAlchemy events:**

Instead of using Pydantic computed fields, BMI and verdict are calculated using SQLAlchemy event listeners that fire before every INSERT and UPDATE:

```python
@event.listens_for(Patient, 'before_insert')
def before_insert(mapper, connection, target):
    target.bmi = calculate_bmi(target.weight, target.height)
    target.verdict = calculate_verdict(target.bmi)

@event.listens_for(Patient, 'before_update')
def before_update(mapper, connection, target):
    target.bmi = calculate_bmi(target.weight, target.height)
    target.verdict = calculate_verdict(target.bmi)
```

This ensures BMI and verdict are **always correct** regardless of how the data is modified.

### Step 3: Restructure Pydantic Schemas (`app/schemas/patient.py`)

Split the original `Patient` schema into three purpose-specific schemas:

| Schema | Purpose |
|--------|---------|
| `PatientCreate` | Validates input for `POST /create` (7 fields, all required) |
| `PatientUpdate` | Validates input for `PUT /edit` (6 fields, all optional) |
| `PatientResponse` | Formats output from DB to API response (9 fields including BMI + verdict) |

`PatientResponse` uses `model_config = {"from_attributes": True}` which tells Pydantic to read data from SQLAlchemy model attributes (e.g., `patient.name`) instead of expecting a dictionary.

### Step 4: Rewrite Routes to Use DB Sessions (`app/routers/patient.py`)

Every route now receives a database session via dependency injection:

```python
@router.get('/view')
def view(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    ...
```

**Key changes per endpoint:**

| Endpoint | Before (JSON) | After (SQLAlchemy) |
|----------|---------------|-------------------|
| GET /view | `data = load_data()` | `db.query(Patient).all()` |
| GET /patient/{id} | `data[patient_id]` | `db.query(Patient).filter(Patient.id == id).first()` |
| GET /sort | `sorted(data.values(), ...)` | `db.query(Patient).order_by(column).all()` |
| POST /create | `data[id] = ...; save_data(data)` | `db.add(patient); db.commit()` |
| PUT /edit/{id} | Manual dict merge + re-serialize | `setattr(patient, key, value); db.commit()` |
| DELETE /delete/{id} | `del data[id]; save_data(data)` | `db.delete(patient); db.commit()` |

### Step 5: Auto-Create Tables on Startup (`app/main.py`)

Added one line to ensure the `patients` table is created when the app starts:

```python
from app.models.patient import Patient  # import so Base knows about this model
Base.metadata.create_all(bind=engine)
```

This is idempotent — if the table already exists, it does nothing.

### Step 6: Tested All Endpoints

Tested via Swagger UI (`/docs`) and direct HTTP requests:

1. **Created 3 patients** → 201 Created, BMI and verdict auto-calculated
2. **Duplicate creation** → 400 Bad Request (correctly rejected)
3. **View all** → Returns dict keyed by patient ID (same format as before)
4. **View single** → Returns patient data with BMI and verdict
5. **404 case** → Returns `{"detail": "Patient not found"}`
6. **Sort by BMI desc** → Database-level sorting, correct order
7. **Update weight** → BMI and verdict auto-recalculated (P003: 17.58→25.39, Underweight→Overweight)
8. **Delete patient** → P002 removed, confirmed via GET /view

---

## Run Command

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

> **Note:** The `patients.db` file is auto-created on first startup. No manual database setup required.
