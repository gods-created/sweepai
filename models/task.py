from .base import Base

from sqlalchemy import String, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str] = mapped_column(String(250), unique=False)
    solution: Mapped[str] = mapped_column(String(250), unique=False, nullable=True, default=None)
    answer: Mapped[str] = mapped_column(String(250), unique=False, nullable=True, default=None)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'))
    subject: Mapped['Subject'] = relationship(back_populates='tasks')
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now())

    __table_args__ = (
        Index('task_title_idx', 'title'),
    )

    def __repr__(self) -> str:
        return 'Task(subject_id: int | str, title: str, description: str, solution: str, answer: str)'

    def __str__(self) -> str:
        return self.title

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'solution': self.solution,
            'answer': self.answer,
            'subject_id': self.subject_id,
            'created_at': self.created_at.strftime('%d.%m.%Y, %H:%M')
        }