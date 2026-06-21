from fastapi import APIRouter, Path, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.models.patient import Patient
from app.models.user import User
from app.database import get_db
from app.utils.auth import get_current_user

# Create a router for all patient-related endpoints
router = APIRouter()


@router.get('/view')
def view(db: Session = Depends(get_db)):
    """Get all patients."""
    # Fetch all patients from the database
    patients = db.query(Patient).all()

    # Convert each patient to a dict with id as key (same format as before)
    result = {}
    for patient in patients:
        patient_data = PatientResponse.model_validate(patient)
        result[patient.id] = patient_data.model_dump(exclude=['id'])

    return result


@router.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', examples=['P001']), db: Session = Depends(get_db)):
    """Get a specific patient by ID."""
    # Look up patient by primary key
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if patient is None:
        raise HTTPException(status_code=404, detail='Patient not found')

    patient_data = PatientResponse.model_validate(patient)
    return patient_data.model_dump(exclude=['id'])


@router.get('/patients/search')
def search_patient(patient_id: str = Query(..., description='ID of the patient to search for'), db: Session = Depends(get_db)):
    """Search for a patient by ID using a query parameter."""
    # Look up patient by primary key
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if patient is None:
        raise HTTPException(status_code=404, detail='Patient not found')

    patient_data = PatientResponse.model_validate(patient)
    return patient_data.model_dump(exclude=['id'])


@router.get('/patients/search/name')
def search_patient_by_name(name: str = Query(..., description='Name of the patient to search for'), db: Session = Depends(get_db)):
    """Search for patients by name (case-insensitive, partial match)."""
    # Look up patients using ilike for case-insensitive partial matching
    patients = db.query(Patient).filter(Patient.name.ilike(f"%{name}%")).all()

    # Return list of patient dicts (empty list if no matches)
    result = []
    for patient in patients:
        patient_data = PatientResponse.model_validate(patient)
        result.append(patient_data.model_dump())

    return result


@router.get('/patients/search/city')
def search_patient_by_city(city: str = Query(..., description='City of the patient to search for'), db: Session = Depends(get_db)):
    """Search for patients by city (case-insensitive)."""
    # Look up patients using ilike for case-insensitive matching
    patients = db.query(Patient).filter(Patient.city.ilike(city)).all()

    # Return list of patient dicts (empty list if no matches)
    result = []
    for patient in patients:
        patient_data = PatientResponse.model_validate(patient)
        result.append(patient_data.model_dump())

    return result


@router.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order'), db: Session = Depends(get_db)):
    """Sort patients by a given field (height, weight, or bmi)."""

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')

    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')

    # Get the column to sort by
    sort_column = getattr(Patient, sort_by)

    # Apply ascending or descending order
    if order == 'desc':
        sort_column = sort_column.desc()

    patients = db.query(Patient).order_by(sort_column).all()

    # Return list of patient dicts (same format as before)
    result = []
    for patient in patients:
        patient_data = PatientResponse.model_validate(patient)
        result.append(patient_data.model_dump())

    return result


@router.post('/create')
def create_patient(patient: PatientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new patient record. (Requires authentication)"""

    # Check if the patient already exists
    existing = db.query(Patient).filter(Patient.id == patient.id).first()
    if existing:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # Create a new Patient model instance
    # bmi and verdict are auto-calculated by the model's before_insert event
    new_patient = Patient(
        id=patient.id,
        name=patient.name,
        city=patient.city,
        age=patient.age,
        gender=patient.gender,
        height=patient.height,
        weight=patient.weight,
        bmi=0,       # placeholder — will be set by before_insert event
        verdict=""   # placeholder — will be set by before_insert event
    )

    # Add to database and commit
    db.add(new_patient)
    db.commit()

    return JSONResponse(status_code=201, content={'message': 'patient created successfully'})


@router.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update an existing patient record (partial update). (Requires authentication)"""

    # Find the patient in the database
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if patient is None:
        raise HTTPException(status_code=404, detail='Patient not found')

    # Get only the fields that were actually sent in the request
    updated_fields = patient_update.model_dump(exclude_unset=True)

    # Update each provided field on the patient model
    for key, value in updated_fields.items():
        setattr(patient, key, value)

    # Commit — bmi and verdict are auto-recalculated by the before_update event
    db.commit()

    return JSONResponse(status_code=200, content={'message': 'patient updated'})


@router.delete('/delete/{patient_id}')
def delete_patient(patient_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a patient record by ID. (Requires authentication)"""

    # Find the patient in the database
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if patient is None:
        raise HTTPException(status_code=404, detail='Patient not found')

    # Delete and commit
    db.delete(patient)
    db.commit()

    return JSONResponse(status_code=200, content={'message': 'patient deleted'})
