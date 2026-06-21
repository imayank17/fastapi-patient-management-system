from pydantic import BaseModel, Field, EmailStr
from typing import Annotated


# Schema for user registration (POST /signup)
class UserCreate(BaseModel):
    username: Annotated[str, Field(..., min_length=3, max_length=50, description='Unique username')]
    email: Annotated[EmailStr, Field(..., description='Valid email address')]
    password: Annotated[str, Field(..., min_length=6, description='Password (min 6 characters)')]


# Schema for user login (POST /login)
class UserLogin(BaseModel):
    email: Annotated[EmailStr, Field(..., description='Registered email address')]
    password: Annotated[str, Field(..., description='Account password')]


# Schema for returning user data in responses (excludes password)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    # Allow Pydantic to read data from SQLAlchemy model attributes
    model_config = {"from_attributes": True}
