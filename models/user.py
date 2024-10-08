from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from sqlalchemy.orm import validates
from datetime import datetime
from utils.db import Base
from enum import Enum as PyEnum

class UserRole(PyEnum):
    ADMIN = "admin"
    ORDINARY = "ordinary"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    fish = Column(String, nullable=False, index=True)
    shaxs = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.ORDINARY)
    password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @validates('password', 'role')
    def validate_password_for_admin(self, key, value):
        if (key == 'role' and value == UserRole.ADMIN and not self.password or
            key == 'password' and self.role == UserRole.ADMIN and not value):
            raise ValueError("Admin users must have a password.")
        return value