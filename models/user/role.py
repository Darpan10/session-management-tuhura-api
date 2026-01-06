from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.db_connect import Base

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "user"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", secondary="user.user_roles", back_populates="roles")
