from sqlalchemy.orm import Session
from app import models,schemas

def get_categories(db: Session) -> list[models.Category]:
    return db.query(models.Category).all()

def get_category(db: Session, category_id: int) -> models.Category | None:
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_category_by_name(db:Session, name: str) -> models.Category | None:
    return db.query(models.Category).filter(models.Category.name == name).first()

def create_category(db: Session, data: schemas.CategoryCreate) -> models.Category:
    obj = models.Category(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete_category(db: Session, category_id: int) -> bool:
    obj = get_category(db, category_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

def update_category(
        db: Session, 
        category_id: int, 
        data:schemas.CategoryUpdate
) -> models.Category | None:
    obj = get_category(db, category_id)
    if not obj:
        return None 
    for k,v in data.model_dump(exclude_unset=True).items():
        setattr(obj,k,v)
    db.commit()
    db.refresh(obj)
    return obj