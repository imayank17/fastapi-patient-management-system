# Feature 8: Patient Search By City API

## What Have Been Done

Added an additional **patient search system** with a `GET /patients/search/city` endpoint. This allows clients to search for patients based on the city they reside in. This endpoint supports **case-insensitive matching**, so users can type the city name without worrying about perfect capitalization.

### Files Modified

| File | What Changed |
|------|-------------|
| `app/routers/patient.py` | Added the `GET /patients/search/city` endpoint utilizing SQLAlchemy's `.ilike()` for filtering. |

### New Endpoint

| Method | Endpoint | Description | Query Parameters | Response |
|--------|----------|-------------|------------------|----------|
| GET | `/patients/search/city` | Search for patients by city | `city` (string, required) | JSON array of patient details |

### Edge Cases Handled

| Scenario | Behavior |
|----------|----------|
| Exact Match (`city=Mumbai`) | Returns a list containing the matching patient(s). |
| Case-Insensitive (`city=mUmBaI`) | Ignores capitalization and returns matching patients. |
| No Matches Found (`city=Chennai`) | Gracefully returns an empty list `[]` with a 200 OK status instead of a 404 error. |
| Missing `city` parameter | FastAPI automatically returns a 422 Validation Error (`Field required`). |

---

## Why Have Been Done

### 1. Improved Filtering Capabilities
In a Patient Management System, users (like hospital administrators) frequently need to filter records by geographic location. Searching by city is a core filtering requirement for generating localized reports or managing regional branches.

### 2. Forgiving Case Sensitivity
City names are often mistyped regarding capitalization (e.g., "new york" instead of "New York"). By making the search case-insensitive, we improve the usability of the API and prevent frustrating "no results found" scenarios caused by minor capitalization errors.

### 3. Consistency with REST Standards
Similar to the name search feature, multiple patients can reside in the same city. Returning a JSON array (even if it's empty when no patients are found) keeps the API consistent and follows standard REST conventions for collection responses.

---

## How Have Been Done

### Step 1: Adding the Search Route (`app/routers/patient.py`)

A new route was added to the patient router. We use FastAPI's `Query` function to declare `city` as a required parameter, and SQLAlchemy's `.ilike()` function to perform the SQL `LIKE` operation for case-insensitivity.

```python
# app/routers/patient.py

@router.get('/patients/search/city')
def search_patient_by_city(city: str = Query(..., description='City of the patient to search for'), db: Session = Depends(get_db)):
    """Search for patients by city (case-insensitive)."""
    
    # 1. Query the database using ilike for exact, case-insensitive match
    # It does not use wildcards (%), meaning "Mumbai" won't match "Navi Mumbai"
    patients = db.query(Patient).filter(Patient.city.ilike(city)).all()

    # 2. Iterate through the results and serialize them
    result = []
    for patient in patients:
        patient_data = PatientResponse.model_validate(patient)
        result.append(patient_data.model_dump(exclude=['id']))

    # 3. Return the list (will be [] if no matches were found)
    return result
```

### Step 2: Testing

Tested the implementation using an automated Python script to ensure it handles various scenarios correctly against mocked data (e.g., a patient in "Mumbai" and another in "Delhi"):

| # | Test | Search Term | Expected Status | Actual Output |
|---|------|-------------|-----------------|---------------|
| 1 | Exact Match | `Mumbai` | 200 OK | ✅ `[{"name": "Rahul", "city": "Mumbai", ...}]` |
| 2 | Mixed Case | `mUmBaI` | 200 OK | ✅ `[{"name": "Rahul", "city": "Mumbai", ...}]` |
| 3 | No Match | `Chennai` | 200 OK | ✅ `[]` |
