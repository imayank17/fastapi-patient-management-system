from fastapi import FastAPI
from app.routers import patient as patient_router
from app.database import engine
from app.models.patient import Patient  # noqa: F401 — import so Base knows about this model

from app.database import Base

# Create all database tables on startup (if they don't exist yet)
Base.metadata.create_all(bind=engine)

# Create the FastAPI application
app = FastAPI(
    title="Patient Management System",
    description="A fully functional API to manage your patient records",
    version="1.0.0"
)

# Register routers
app.include_router(patient_router.router)


@app.get("/")
def hello():
    return {'message': 'Patient Management System API'}


@app.get('/about')
def about():
    return {'message': 'A fully functional API to manage your patient records'}
