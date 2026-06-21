from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import patient as patient_router
from app.routers import auth as auth_router
from app.database import engine
from app.models.patient import Patient 
from app.models.user import User  

from app.database import Base

# Create all database tables on startup (if they don't exist yet)
Base.metadata.create_all(bind=engine)

# Create the FastAPI application
app = FastAPI(
    title="Patient Management System",
    description="A fully functional API to manage your patient records",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Register routers
app.include_router(patient_router.router)
app.include_router(auth_router.router)


@app.get("/")
def hello():
    return {'message': 'Patient Management System API'}


@app.get('/about')
def about():
    return {'message': 'A fully functional API to manage your patient records'}
