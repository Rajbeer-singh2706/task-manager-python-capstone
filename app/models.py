from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String, default="#3B82F6")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="category")

class Task(Base):
    """Minimal stub for now — full Task fields (title, status, priority, etc.)
    will be added when we build the Tasks functionality next."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )

    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="tasks")
    