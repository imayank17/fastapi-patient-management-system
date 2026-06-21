# Feature 4: User Login API

## What Have Been Done

Added a **user login system** with a `POST /login` endpoint. Users can now authenticate by providing their registered email and password. The system verifies the credentials against the securely hashed password stored in the database.

### Files Modified

| File | What Changed |
|------|-------------|
| `app/schemas/auth.py` | Added `UserLogin` Pydantic schema for login request validation |
| `app/routers/auth.py` | Added `verify_password` helper and `POST /login` endpoint |

### New Endpoint

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|-------------|----------|
| POST | `/login` | Authenticate a user | `{email, password}` | `{message: "Login successful"}` |

### Error Handling

| Scenario | Status Code | Error Message |
|----------|-------------|---------------|
| Incorrect password | 401 | `"Invalid email or password"` |
| Email not registered | 401 | `"Invalid email or password"` |
| Invalid email format | 422 | Validation error (`value is not a valid email address`) |
| Missing required fields | 422 | Validation error |

---

## Why Have Been Done

### 1. Essential Authentication Step

Following the user registration feature (Feature 3), a login endpoint is the necessary next step to allow existing users to access the system. It verifies that a user is who they claim to be.

### 2. Secure Credential Verification

The login endpoint uses `bcrypt.checkpw()` to securely compare the plain-text password provided by the user with the hashed password stored in the database. This ensures that:
- Passwords are never compared in plain text.
- Even if the database is exposed, the actual passwords cannot be easily deduced.

### 3. Vague Error Messages for Security

When a login attempt fails (whether due to a wrong password or a non-existent email), the API intentionally returns a generic `401 Unauthorized` error with the message `"Invalid email or password"`.
This prevents "user enumeration" attacks, where an attacker could use the login endpoint to discover which email addresses are registered in the system.

### 4. Input Validation

By using the `UserLogin` schema with `EmailStr`, the API automatically validates the format of the email before even hitting the database, saving resources and preventing malformed queries.

---

## How Have Been Done

### Step 1: Added Login Schema (`app/schemas/auth.py`)

Created a new `UserLogin` schema specifically for the login request. It requires an email and a password:

```python
# app/schemas/auth.py

class UserLogin(BaseModel):
    email: Annotated[EmailStr, Field(..., description='Registered email address')]
    password: Annotated[str, Field(..., description='Account password')]
```

### Step 2: Added Password Verification Helper (`app/routers/auth.py`)

Created a helper function to verify passwords using `bcrypt`:

```python
# app/routers/auth.py
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
```

### Step 3: Created the Login Route (`app/routers/auth.py`)

Implemented the `POST /login` endpoint. The flow is as follows:

1.  Validate input via `UserLogin` schema.
2.  Query the database for a user with the provided email.
3.  If the user is not found, return `401`.
4.  If the user is found, use `verify_password` to check the provided password against the stored hash.
5.  If the password doesn't match, return `401`.
6.  If the password matches, return a success message.

```python
# app/routers/auth.py

@router.post('/login')
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""

    # Find user by email
    existing_user = db.query(User).filter(User.email == user.email).first()

    # If email not found, return error
    if existing_user is None:
        raise HTTPException(status_code=401, detail='Invalid email or password')

    # Verify the password against the stored hash
    if not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=401, detail='Invalid email or password')

    # Login successful
    return {'message': 'Login successful'}
```

### Step 4: Tested Scenarios

All scenarios were successfully tested via Swagger UI (`/docs`):

| # | Test | Input | Expected | Actual |
|---|------|-------|----------|--------|
| 1 | Valid login | `mayank@example.com / test123` | 200 OK | ✅ `{"message": "Login successful"}` |
| 2 | Wrong password | `mayank@example.com / wrongpass` | 401 Unauthorized | ✅ `"Invalid email or password"` |
| 3 | Non-existent email | `nobody@example.com / test123` | 401 Unauthorized | ✅ `"Invalid email or password"` |
| 4 | Invalid email format | `not-an-email / test123` | 422 Unprocessable Entity | ✅ Validation error |

---

