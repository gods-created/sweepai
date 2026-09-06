from .base import Base

from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from typing import List

from datetime import datetime

from argon2 import PasswordHasher

class Teacher(Base):
    __tablename__ = 'teachers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password: Mapped[str] = mapped_column(String(250), unique=True)
    fullname: Mapped[str] = mapped_column(String(150), unique=False)
    subjects: Mapped[List['Subject']] = relationship(back_populates='teacher', cascade='all, delete-orphan')
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now())

    @validates('password')
    def validate_password(self, key: str, value: str) -> str:
        ph = PasswordHasher()
        return ph.hash(value)

    __table_args__ = (
        Index('password_email_idx', 'email', 'password'),
    )

    def __repr__(self) -> str:
        return 'Teacher(email: str, password: str, fullname: str)'

    def __str__(self) -> str:
        return self.email

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'email': self.email,
            'fullname': self.fullname,
            'subjects': [subject.to_json() for subject in self.subjects],
            'created_at': self.created_at.strftime('%d.%m.%Y, %H:%M')
        }