from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings  # your Pydantic settings
import socket

# Enable IPv6 for socket connections
# socket.getaddrinfo = lambda *args, **kwargs: [
#     (socket.AF_INET6 if family == socket.AF_UNSPEC else family, *rest)
#     for family, *rest in socket.getaddrinfo(*args, **kwargs)
# ]

# Build the database URL from Pydantic settings
DATABASE_URL = (
    f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

# Create SQLAlchemy engine with connection arguments for better compatibility
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()