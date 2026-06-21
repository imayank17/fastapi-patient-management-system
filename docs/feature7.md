# Feature 7: Patient Search By Name API

## What Have Been Done

Added an enhanced **patient search system** with a `GET /patients/search/name` endpoint. This allows clients to search for patients using their name. Unlike the ID search, this endpoint supports **case-insensitive, partial matching**, meaning users do not need to type the exact or complete name to find a record.

### Files Modified

| File | What Changed |
|------|-------------|
| `app/routers/patient.py` | Added the `GET /patients/search/name` endpoint utilizing SQLAlchemy's `.ilike()` for filtering. |

### New Endpoint

| Method | Endpoint | Description | Query Parameters | Response |
|--------|----------|-------------|------------------|----------|
| GET | `/patients/search/name` | Search for patients by name | `name` (string, required) | JSON array of patient details |

### Edge Cases Handled

| Scenario | Behavior |
|----------|----------|
| Exact Match (`name=Ananya Sharma`) | Returns a list containing the matching patient(s). |
| Partial Match (`name=nanya`) | Returns a list of all patients whose name contains "nanya". |
| Case-Insensitive (`name=aNaNyA`) | Ignores capitalization and returns matching patients. |
| No Matches Found (`name=Zebra`) | Gracefully returns an empty list `[]` with a 200 OK status instead of a 404 error. |
| Missing `name` parameter | FastAPI automatically returns a 422 Validation Error (`Field required`). |

---

## Why Have Been Done

### 1. Improved User Experience
Searching by an exact, alphanumeric `patient_id` (like `P001`) is often impractical for human users. Searching by name is a far more natural and common requirement for a Patient Management System.

### 2. Flexible Queries (Partial & Case-Insensitive)
Users rarely type exact names with perfect capitalization. By allowing partial matches (e.g., typing "john" to find "Johnathan Doe"), the system becomes significantly more forgiving and robust.

### 3. Collection Response
Because multiple patients might share the same name (or part of a name), this endpoint correctly returns a JSON array (a list of patients) rather than a single object. If no patients match, returning an empty list `[]` is the standard RESTful approach for collection queries, as opposed to throwing a `404 Not Found` error.

---

## How Have Been Done

### Step 1: Adding the Search Route (`app/routers/patient.py`)

A new route was added to the patient router. We use FastAPI's `Query` function to declare `name` as a required parameter, and SQLAlchemy's `.ilike()` function to perform the SQL `LIKE` operation while ignoring case.

```python
# app/routers/patient.py

@router.get('/patients/search/name')
def search_patient_by_name(name: str = Query(..., description='Name of the patient to search for'), db: Session = Depends(get_db)):
    """Search for patients by name (case-insensitive, partial match)."""
    
    # 1. Query the database using ilike for partial, case-insensitive match
    # f"%{name}%" surrounds the search term with SQL wildcards
    patients = db.query(Patient).filter(Patient.name.ilike(f"%{name}%")).all()

    # 2. Iterate through the results and serialize them
    result = []
    for patient in patients:
        patient_data = PatientResponse.model_validate(patient)
        result.append(patient_data.model_dump(exclude=['id']))

    # 3. Return the list (will be [] if no matches were found)
    return result
```

### Step 2: Testing

Tested the implementation using an automated Python script to ensure it handles various scenarios correctly against mocked data (e.g., "Ananya Sharma"):

| # | Test | Search Term | Expected Status | Actual Output |
|---|------|-------------|-----------------|---------------|
| 1 | Exact Match | `Ananya Sharma` | 200 OK | ✅ `[{"name": "Ananya Sharma", ...}]` |
| 2 | Partial & Mixed Case | `aNaNyA` | 200 OK | ✅ `[{"name": "Ananya Sharma", ...}]` |
| 3 | No Match | `Zebra` | 200 OK | ✅ `[]` |
