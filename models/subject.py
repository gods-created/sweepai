from .base import Base

from sqlalchemy import String, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List

from datetime import datetime

class Subject(Base):
    __tablename__ = 'subjects'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), unique=False)
    tasks: Mapped[List['Task']] = relationship(back_populates='subject', cascade='all, delete-orphan')
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id'))
    teacher: Mapped['Teacher'] = relationship(back_populates='subjects')
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now())

    __table_args__ = (
        Index('subject_title_idx', 'title'),
    )

    def __repr__(self) -> str:
        return 'Subject(teacher_id: int | str, title: str)'

    def __str__(self) -> str:
        return self.title

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'tasks': [task.to_json() for task in self.tasks],
            'teacher_id': self.teacher_id,
            'created_at': self.created_at.strftime('%d.%m.%Y, %H:%M')
        }