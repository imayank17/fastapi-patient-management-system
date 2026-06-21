from sqlalchemy import Column, String, Integer, Float, event
from app.database import Base


# Helper functions to calculate BMI and verdict
def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (m)."""
    return round(weight / (height ** 2), 2)


def calculate_verdict(bmi):
    """Determine health verdict based on BMI value."""
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 25:
        return 'Normal'
    elif bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'


# SQLAlchemy model for the patients table
class Patient(Base):
    __tablename__ = 'patients'

    id = Column(String, primary_key=True, index=True)     # e.g. "P001"
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    height = Column(Float, nullable=False)                 # in meters
    weight = Column(Float, nullable=False)                 # in kgs
    bmi = Column(Float, nullable=False)                    # auto-calculated
    verdict = Column(String, nullable=False)               # auto-calculated


# Automatically calculate bmi and verdict before INSERT
@event.listens_for(Patient, 'before_insert')
def before_insert(mapper, connection, target):
    """Auto-calculate BMI and verdict when a new patient is created."""
    target.bmi = calculate_bmi(target.weight, target.height)
    target.verdict = calculate_verdict(target.bmi)


# Automatically recalculate bmi and verdict before UPDATE
@event.listens_for(Patient, 'before_update')
def before_update(mapper, connection, target):
    """Auto-recalculate BMI and verdict when a patient is updated."""
    target.bmi = calculate_bmi(target.weight, target.height)
    target.verdict = calculate_verdict(target.bmi)
