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
* Email validation and mail service integration
* Secure password hashing with bcrypt and argon2

---

## Requirements

* **Python 3.12.10**
* PostgreSQL
* Virtual environment (recommended)
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

**Note:** This project was developed and tested with **Python 3.12.10**.

---

### 3. Install dependencies

A `requirements.txt` file is included in the project with all required packages and their specific versions. Install all dependencies using:

```bash
pip install -r requirements.txt
```

This will install the following packages:

```
annotated-doc==0.0.3
annotated-types==0.7.0
anyio==4.11.0
argon2-cffi==25.1.0
argon2-cffi-bindings==25.1.0
bcrypt==5.0.0
blinker==1.9.0
certifi==2025.11.12
cffi==2.0.0
charset-normalizer==3.4.4
click==8.3.0
colorama==0.4.6
cryptography==46.0.3
dnspython==2.8.0
ecdsa==0.19.1
email-validator==2.3.0
fastapi==0.121.0
Flask==3.1.2
greenlet==3.2.4
h11==0.16.0
httptools==0.7.1
icalendar==6.3.2
idna==3.11
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.3
passlib==1.7.4
psycopg2-binary==2.9.11
pyasn1==0.6.1
pycparser==2.23
pydantic==2.12.4
pydantic_core==2.41.5
pydantic-settings==2.12.0
python-dateutil==2.9.0.post0
python-dotenv==1.2.1
python-jose==3.5.0
python-multipart==0.0.20
PyYAML==6.0.3
requests==2.32.5
rsa==4.9.1
six==1.17.0
sniffio==1.3.1
SQLAlchemy==2.0.44
starlette==0.49.3
typing_extensions==4.15.0
typing-inspection==0.4.2
tzdata==2025.3
urllib3==2.5.0
uvicorn==0.38.0
watchfiles==1.1.1
websockets==15.0.1
Werkzeug==3.1.3
```

Verify installation:

```bash
pip list
```

---

### 4. Create `.env` file


Create a `.env` file in the project root with required variables:

```env
APP_NAME=Session Management API
DEBUG=True
DATABASE_URL=postgresql://username:password@localhost:5432/session_db
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
JWT_SECRET=your_jwt_secret_key
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_FROM=your_email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.example.com
```

**Important:** Replace the placeholder values with your actual credentials.

---

### 5. Database Setup

Ensure PostgreSQL is installed and running on your system. Create a database for the application:

```sql
CREATE DATABASE session_db;
```

Update the `DATABASE_URL` in your `.env` file with your PostgreSQL credentials.

---

### 6. Run the backend server

Start the development server:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

```
http://127.0.0.1:8000
```

API documentation (Swagger UI) is accessible at:

```
http://127.0.0.1:8000/docs
```

Alternative documentation (ReDoc):

```
http://127.0.0.1:8000/redoc
```

---

## Project Structure

```
session-management-tuhura-api-main/
├── main.py                    # FastAPI application entry point
├── config.py                  # Application configuration
├── requirements.txt           # Python dependencies with versions
├── test_main.http             # HTTP test requests
├── api/
│   ├── __init__.py
│   └── auth_controller.py     # Authentication routes
├── core/
│   ├── __init__.py
│   ├── auth_config.py         # Auth configuration
│   └── db_connect.py          # Database connection
├── dependencies/
│   ├── __init__.py
│   └── db_dependency.py       # Database dependencies
├── models/
│   ├── __init__.py
│   └── user/
│       ├── __init__.py
│       ├── role.py            # Role model
│       ├── user_role.py       # User-Role relationship
│       └── user.py            # User model
├── schemas/
│   ├── __init__.py
│   └── user_schema.py         # Pydantic schemas
├── services/
│   ├── __init__.py
│   ├── auth_service.py        # Authentication service
│   └── mail_service.py        # Email service
└── utils/
    ├── __init__.py
    └── jwt_utils.py           # JWT token utilities
```

---

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.121.0 | Modern web framework for building APIs |
| Uvicorn | 0.38.0 | ASGI server for running FastAPI |
| SQLAlchemy | 2.0.44 | ORM for database operations |
| Pydantic | 2.12.4 | Data validation and settings management |
| psycopg2-binary | 2.9.11 | PostgreSQL database adapter |
| python-jose | 3.5.0 | JWT token creation and verification |
| passlib | 1.7.4 | Password hashing utilities |
| bcrypt | 5.0.0 | Password hashing algorithm |
| argon2-cffi | 25.1.0 | Alternative password hashing |
| email-validator | 2.3.0 | Email address validation |
| python-dotenv | 1.2.1 | Environment variable management |

---

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and receive JWT token
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user information
- `POST /api/auth/refresh` - Refresh JWT token

Refer to `/docs` for complete API documentation.

---

## Testing

Install testing packages:

```bash
pip install pytest pytest-asyncio httpx
```

Run tests:

```bash
pytest
```

---

## Development Notes

* Ensure PostgreSQL is running and accessible using the credentials in `.env`
* Adjust `ALLOWED_ORIGINS` for production deployment
* Use **Postman**, **Thunder Client**, or the built-in `/docs` Swagger UI for API testing
* The application uses both bcrypt and argon2 for secure password hashing
* JWT tokens are used for stateless authentication
* Email service is configured for user notifications

---

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in your `.env` file
2. Use a production-grade ASGI server configuration
3. Set up proper CORS origins
4. Use environment variables for sensitive data
5. Configure a production PostgreSQL database
6. Set up SSL/TLS certificates
7. Use a reverse proxy (e.g., Nginx) in front of Uvicorn

---

## Troubleshooting

**Database connection errors:**
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure the database exists

**Import errors:**
- Verify all dependencies are installed: `pip list`
- Ensure Python 3.12.10 is being used: `python --version`
- Reactivate virtual environment

**JWT token errors:**
- Verify `JWT_SECRET` is set in `.env`
- Check token expiration settings in auth configuration

---

## License

This project is part of the Tuhura Tech session management system.

---

## Support

For issues and questions, please refer to the project documentation or contact the development team.


