# Feature 3: User Registration (Signup)

## What Have Been Done

Added a **user registration system** with a `POST /signup` endpoint. Users can now create accounts with a username, email, and password. Passwords are securely hashed using **bcrypt** before being stored in the database.

### Files Created

| File | Purpose |
|------|---------|
| `app/models/user.py` | SQLAlchemy `User` model with users table |
| `app/schemas/auth.py` | `UserCreate` and `UserResponse` Pydantic schemas |
| `app/routers/auth.py` | `POST /signup` endpoint with validation and hashing |

### Files Modified

| File | What Changed |
|------|-------------|
| `app/main.py` | Imported `User` model and registered `auth_router` |
| `requirements.txt` | Added `bcrypt` and `pydantic[email]` |

### Updated Folder Structure

```
fastapi-demo-api/
├── app/
│   ├── __init__.py
│   ├── main.py               # Added: auth router registration + User model import
│   ├── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── patient.py
│   │   └── user.py            # [NEW] SQLAlchemy User model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── patient.py
│   │   └── auth.py            # [NEW] UserCreate + UserResponse schemas
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── patient.py
│   │   └── auth.py            # [NEW] POST /signup endpoint
│   │
│   └── services/
│       └── __init__.py
│
├── patients.db
├── requirements.txt            # Added: bcrypt, pydantic[email]
└── ...
```

### User Table Schema

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | Integer | Primary key, auto-increment |
| `username` | String | Unique, not null, indexed |
| `email` | String | Unique, not null, indexed |
| `password` | String | Not null (stores bcrypt hash) |

### New Endpoint

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|-------------|----------|
| POST | `/signup` | Register a new user | `{username, email, password}` | `{id, username, email}` |

### Validation Rules

| Field | Rule |
|-------|------|
| `username` | Required, 3–50 characters |
| `email` | Required, must be a valid email format (uses `EmailStr`) |
| `password` | Required, minimum 6 characters |

### Error Handling

| Scenario | Status Code | Error Message |
|----------|-------------|---------------|
| Duplicate username | 400 | `"Username already exists"` |
| Duplicate email | 400 | `"Email already registered"` |
| Invalid email format | 422 | `"value is not a valid email address"` |
| Short password (<6 chars) | 422 | Validation error (min_length) |
| Missing required fields | 422 | Validation error |

---

## Why Have Been Done

### 1. Foundation for Authentication

User registration is the **first step** toward a complete authentication system. Before users can log in (JWT), they need to be able to create accounts. This feature lays the groundwork for:
- Login endpoint (coming next)
- JWT token generation
- Protected routes

### 2. Secure Password Storage

Passwords are **never stored as plain text**. Using bcrypt:
- Passwords are hashed with a random salt
- The hash is one-way — you cannot reverse it to get the original password
- Even if the database is compromised, passwords remain safe

Example of what gets stored:
```
Plain:  "test123"
Stored: "$2b$12$LJ3m4ys4Lz5F6K8vJ7qXxO9QgYfHnR2kL1mN3oP4qR5sT6uV7wX8"
```

### 3. Email Validation with Pydantic

Using `EmailStr` from pydantic provides:
- Format validation (must have `@` and valid domain)
- DNS-level validation (checks if the domain exists)
- Rejects obviously invalid inputs like `"not-an-email"`

### 4. Duplicate Prevention

Both `username` and `email` have **unique constraints** at two levels:
- **Database level** — `unique=True` on the SQLAlchemy column prevents duplicates even if the application check fails
- **Application level** — Explicit checks in the route give user-friendly error messages instead of raw database errors

### 5. Response Security

The `UserResponse` schema **excludes the password field**, ensuring that even the hashed password is never sent back to the client in API responses.

---

## How Have Been Done

### Step 1: Created the User Model (`app/models/user.py`)

Defined a simple SQLAlchemy model with 4 columns:

```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)  # stores hashed password
```

Key decisions:
- `id` uses `autoincrement=True` — no need to manually assign IDs
- `username` and `email` are `indexed` for fast lookups during duplicate checks
- `unique=True` provides database-level duplicate protection

### Step 2: Created Auth Schemas (`app/schemas/auth.py`)

Two schemas for input and output:

```python
from pydantic import BaseModel, Field, EmailStr

# Input — what the user sends
class UserCreate(BaseModel):
    username: Annotated[str, Field(..., min_length=3, max_length=50)]
    email: Annotated[EmailStr, Field(...)]
    password: Annotated[str, Field(..., min_length=6)]

# Output — what the API returns (no password!)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}
```

`EmailStr` comes from `pydantic[email]` and automatically validates email format.

### Step 3: Created the Signup Route (`app/routers/auth.py`)

The signup endpoint follows this flow:

```
User sends POST /signup with {username, email, password}
    ↓
Pydantic validates the input (email format, password length)
    ↓
Check if username already exists → 400 if yes
    ↓
Check if email already exists → 400 if yes
    ↓
Hash the password using bcrypt
    ↓
Create User object and save to database
    ↓
Return {id, username, email} (no password in response)
```

Password hashing uses `bcrypt` directly:

```python
import bcrypt

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')
```

> **Note:** We used `bcrypt` directly instead of `passlib` because `passlib` is unmaintained and incompatible with `bcrypt>=5.0`.

### Step 4: Registered in `main.py`

Added two lines to the entry point:

```python
from app.routers import auth as auth_router
from app.models.user import User

app.include_router(auth_router.router)
```

The `User` model import ensures SQLAlchemy's `Base` knows about the `users` table so it gets created automatically by `Base.metadata.create_all()`.

### Step 5: Tested All Scenarios

Tested via Swagger UI (`/docs`):

| # | Test | Input | Expected | Actual |
|---|------|-------|----------|--------|
| 1 | Valid signup | `mayank / mayank@example.com / test123` | 201 Created | ✅ `{id:1, username, email}` |
| 2 | Duplicate username | `mayank / other@example.com / test456` | 400 | ✅ `"Username already exists"` |
| 3 | Duplicate email | `newuser / mayank@example.com / test789` | 400 | ✅ `"Email already registered"` |
| 4 | Invalid email | `testuser / not-an-email / test123` | 422 | ✅ Validation error |
| 5 | Second valid signup | `admin / admin@example.com / admin123` | 201 Created | ✅ `{id:2, username, email}` |

---

## Dependencies Added

| Package | Purpose |
|---------|---------|
| `bcrypt` | Secure password hashing using the bcrypt algorithm |
| `pydantic[email]` | Provides `EmailStr` type for email validation |

Install with:
```bash
pip install bcrypt "pydantic[email]"
```

---


