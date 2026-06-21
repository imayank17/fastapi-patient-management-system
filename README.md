# FastAPI + React Patient Management System

A full-stack, modular Patient Management System built with **FastAPI** on the backend and **React (Vite)** on the frontend. The application features full CRUD operations, JWT authentication, searching and sorting capabilities, and SQLite database storage using SQLAlchemy.

---

## 🌟 Features

### Backend (FastAPI)
- **Modular Architecture:** Clean separation of concerns (`models`, `schemas`, `routers`, `utils`).
- **Database:** SQLAlchemy ORM integrated with SQLite (`patients.db`).
- **Authentication:** Secure user registration and login using bcrypt password hashing and JWT (JSON Web Tokens).
- **Protected Routes:** Dependency-injected endpoint protection requiring valid JWT Bearer tokens for mutating data.
- **Smart Data:** Auto-calculation of BMI and verdict (Underweight, Normal, Overweight, Obese) using database event listeners (`before_insert`, `before_update`).
- **Advanced Querying:** Search endpoints by ID, Name (partial/case-insensitive), and City. Sorting endpoints by height, weight, and BMI.
- **CORS Configured:** Out-of-the-box readiness to accept cross-origin requests from the frontend.

### Frontend (React + Vite)
- **Fast Build Tool:** Scaffolded using Vite for lightning-fast hot module replacement.
- **Client-Side Routing:** Managed via `react-router-dom` (Login, Signup, Dashboard).
- **API Integration:** Centralized Axios instance with HTTP interceptors that automatically inject JWT tokens into protected requests.
- **Interactive UI:** 
  - Dynamic Dashboard listing all patients.
  - Interactive Search/Filter bar.
  - Add/Edit Modals for quick record mutations without leaving the page.
  - Clean, responsive plain CSS styling.

---

## 🚀 Quick Start Guide

This project is separated into two distinct directories: `/backend` and `/frontend`. You will need two separate terminal windows to run both the API and the React client simultaneously.

### 1. Setting up the Backend

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment:**
   - **Linux / macOS:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   > The backend will start on `http://127.0.0.1:8000`. You can view the interactive API documentation at `http://127.0.0.1:8000/docs`.

---

### 2. Setting up the Frontend

1. **Open a new terminal window** and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. **Install Node Modules:**
   Make sure you have [Node.js](https://nodejs.org/) installed, then run:
   ```bash
   npm install
   ```

3. **Start the Development Server:**
   ```bash
   npm run dev
   ```
   > The frontend will start on `http://localhost:5173`. 

---

## 📖 Using the Application

1. Open your browser to `http://localhost:5173`.
2. You will be redirected to the `/login` page.
3. Click **"Sign up"** to create a new user account (e.g., admin / admin123).
4. **Log in** with your new credentials.
5. You are now on the **Dashboard**! You can:
   - Click **"+ Add Patient"** to insert records.
   - Use the **Search bar** to filter the list.
   - Click **Edit** to modify records (BMI and verdict will update automatically).
   - Click **Delete** to remove records.

---

## 📂 Project Structure

```text
fastapi-demo-api/
│
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── models/           # SQLAlchemy DB Models (Patient, User)
│   │   ├── routers/          # API Route Controllers
│   │   ├── schemas/          # Pydantic Validation Schemas
│   │   ├── utils/            # JWT & Security Utilities
│   │   ├── database.py       # DB Connection Setup
│   │   └── main.py           # Application Entrypoint & CORS
│   │
│   ├── patients.db           # SQLite Database
│   ├── requirements.txt      # Python Dependencies
│   └── feature*.md           # Documentation of development phases
│
└── frontend/                 # React Vite Application
    ├── package.json          # Node Dependencies
    ├── index.html            # Vite HTML Template
    └── src/
        ├── App.jsx           # Main Router Component
        ├── index.css         # Global Stylesheet
        ├── main.jsx          # React Entrypoint
        ├── pages/            # View Components (Login, Signup, Patients)
        └── services/         # Axios API Configuration (`api.js`)
```

---

## 🛡️ Security Note
The `SECRET_KEY` for JWT signing currently resides hard-coded in `backend/app/utils/auth.py`. 
For production environments, ensure you extract this to a `.env` file using a library like `python-dotenv` or `pydantic-settings` to prevent exposing your signing keys.
