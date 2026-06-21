# Feature 5: JWT Authentication

## What Have Been Done

Implemented a complete **JSON Web Token (JWT) authentication** system. The `POST /login` endpoint now returns a signed JWT upon successful authentication, which the client can use to access protected endpoints. Mutation endpoints (`POST`, `PUT`, `DELETE`) are now protected and require a valid JWT, while read endpoints (`GET`) remain public.

### Files Created

| File | Purpose |
|------|---------|
| `app/utils/__init__.py` | Initializes the utils package |
| `app/utils/auth.py` | Contains JWT creation (`create_access_token`) and the `get_current_user` dependency for route protection. |

### Files Modified

| File | What Changed |
|------|-------------|
| `app/schemas/auth.py` | Added `Token` Pydantic schema for the login response. |
| `app/routers/auth.py` | Modified `login` endpoint to return a JWT access token instead of a simple success message. |
| `app/routers/patient.py` | Added `current_user: User = Depends(get_current_user)` to `create_patient`, `update_patient`, and `delete_patient` routes to protect them. |
| `requirements.txt` | Added `python-jose[cryptography]` for JWT handling. |

### Updated Folder Structure

```
fastapi-demo-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   │
│   ├── services/
│   │
│   └── utils/               # [NEW] Utilities package
│       ├── __init__.py
│       └── auth.py          # [NEW] JWT utilities and dependencies
│
├── patients.db
└── requirements.txt         # Added: python-jose[cryptography]
```

### Endpoints Overview

| Method | Endpoint | Protected? | Description |
|--------|----------|------------|-------------|
| POST | `/signup` | ❌ No | Register a new user |
| POST | `/login` | ❌ No | Authenticate and get JWT token |
| GET | `/view` | ❌ No | Get all patients (Public) |
| GET | `/patient/{id}` | ❌ No | Get specific patient (Public) |
| GET | `/sort` | ❌ No | Sort patients (Public) |
| POST | `/create` | ✅ Yes | Create new patient (Requires Token) |
| PUT | `/edit/{id}` | ✅ Yes | Edit patient (Requires Token) |
| DELETE | `/delete/{id}`| ✅ Yes | Delete patient (Requires Token) |

---

## Why Have Been Done

### 1. Stateless Authentication

JWTs provide a stateless authentication mechanism. The server does not need to store active sessions in a database or memory. The token itself contains all the necessary information (in this case, the user's email as the `sub` claim) and is cryptographically signed to prevent tampering.

### 2. Route Protection

By using FastAPI's dependency injection (`Depends(get_current_user)`), we can easily protect specific routes. The dependency automatically:
- Extracts the token from the `Authorization: Bearer <token>` header.
- Verifies the signature using the `SECRET_KEY`.
- Checks if the token is expired.
- Decodes the payload to find the user in the database.
- Rejects the request with a `401 Unauthorized` if any of the above fails.

### 3. Public vs. Private Data

We kept the `GET` routes public, meaning anyone can view the patient directory. However, we secured the mutation routes (`POST`, `PUT`, `DELETE`) so that only authenticated users (e.g., doctors or admins) can modify patient records.

---

## How Have Been Done

### Step 1: JWT Utilities (`app/utils/auth.py`)

Created the core logic for generating and verifying tokens using `python-jose`:

```python
from jose import jwt
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "my-super-secret-key-please-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):
    # Sets expiration and encodes the JWT using the secret key
    ...

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Decodes token, extracts user email, and fetches user from DB
    ...
```

### Step 2: Update Login Response (`app/schemas/auth.py` & `app/routers/auth.py`)

Added the `Token` schema and updated the `/login` route to generate the token on successful password verification:

```python
# app/schemas/auth.py
class Token(BaseModel):
    access_token: str
    token_type: str

# app/routers/auth.py
@router.post('/login', response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    ...
    # Verify password...
    access_token = create_access_token(data={"sub": existing_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
```

### Step 3: Protect Patient Routes (`app/routers/patient.py`)

Injected the `get_current_user` dependency into the mutation endpoints. If a user is not authenticated, FastAPI automatically returns a `401 Unauthorized` before the function body even executes.

```python
from app.utils.auth import get_current_user
from app.models.user import User

@router.post('/create')
def create_patient(patient: PatientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Only executes if current_user is successfully resolved from a valid JWT
    ...
```

### Step 4: Testing

Tested the implementation with a Python script utilizing `urllib`:
1.  **Signup:** Created a new user `admin@example.com`.
2.  **Login:** Received a valid JWT string.
3.  **Public Route:** Accessed `GET /view` without a token successfully (200).
4.  **Protected Route (No Token):** Attempted `POST /create` without an `Authorization` header. Received `401 Unauthorized` (`Not authenticated`).
5.  **Protected Route (With Token):** Passed the JWT in the `Authorization: Bearer <token>` header to `POST /create` and `DELETE /delete/{id}`. Both succeeded successfully.

---

## Dependencies Added

| Package | Purpose |
|---------|---------|
| `python-jose[cryptography]` | Standard library for JSON Web Signature (JWS) and JSON Web Encryption (JWE) used to encode and decode JWTs. |

Install with:
```bash
pip install "python-jose[cryptography]"
```
