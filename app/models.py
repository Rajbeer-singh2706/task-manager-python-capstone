from app.database import Base


class Category(Base):
    __tablename__ = "categories" 


class Task(Base):
    """Minimal stub for now — full Task fields (title, status, priority, etc.)
    will be added when we build the Tasks functionality next."""
    __tablename__ = "tasks"
    