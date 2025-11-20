# Session Management Backend

This repository contains the **backend API** for the Session Management web application, built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. It handles user authentication, session tracking, and data persistence for the frontend application.

---

## Features

* User registration and login
* JWT-based authentication
* Session management APIs
* PostgreSQL database integration
* CORS configured for frontend development
* Configurable settings via `.env`

---

## Requirements

* Python 3.12+
* PostgreSQL
* pip packages (listed below)
* React frontend (separate repository)

---

## Setup

### 1. Clone the repository:

```bash
git clone https://github.com/your-username/session-management-backend.git
cd session-management-backend
```

### 2. Configure Python Interpreter

Create a virtual environment and activate it:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

Check the interpreter and Python version:

```bash
python --version
pip --version
```

---

### 3. Install dependencies

You can install all required packages with specific versions:

```bash
pip install fastapi==0.111.1 \
            uvicorn==0.23.2 \
            pydantic==2.6.1 \
            sqlalchemy==2.0.22 \
            alembic==1.11.1 \
            psycopg2-binary==2.9.7 \
            python-dotenv==1.0.1 \
            passlib[bcrypt]==1.8.2 \
            email-validator \
            bcrypt \
            python-jose[cryptography] \
            python-multipart
```

Optional/alternative versions:

```bash
pip install fastapi==0.111.1
pip install sqlalchemy==2.0.44
pip install alembic==1.11.1
pip install psycopg2-binary==2.9.9
pip install passlib[bcrypt]==1.7.4
```

Check installed versions:

```bash
pip list
```

---

### 4. Create `.env` file

Create a `.env` in the project root with required variables:

```env
APP_NAME=Session Management API
DEBUG=True
DATABASE_URL=postgresql://username:password@localhost:5432/session_db
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
JWT_SECRET=your_jwt_secret_key
```

---

### 5. Run the backend server

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API documentation available at:

```
http://127.0.0.1:8000/docs
```

---

### 6. Testing

Install testing packages:

```bash
pip install pytest pytest-asyncio httpx
```

Run tests:

```bash
pytest
```

---

## Project Structure

```
├── main.py             # FastAPI entry point
├── api/                # API route modules
│   └── auth_controller.py
├── core/               # Core modules (DB connection, utilities)
│   └── db_connect.py
├── models/             # SQLAlchemy models
├── schemas/            # Pydantic request/response schemas
├── config.py           # Settings and environment variables
├── requirements.txt    # Python dependencies
└── README.md
```

---

## Notes

* Ensure PostgreSQL is running and accessible using the credentials in `.env`.
* Adjust `ALLOWED_ORIGINS` for production deployment.
* Use **Postman** or the built-in `/docs` Swagger UI for API testing.

