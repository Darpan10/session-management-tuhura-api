from sqlalchemy import Column, Integer, ForeignKey
from core.db_connect import Base

class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "user"}

    user_id = Column(Integer, ForeignKey("user.users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("user.roles.id"), primary_key=True)
