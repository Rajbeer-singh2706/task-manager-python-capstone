from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db


router = APIRouter()

@router.get("/", response_model=list[schemas.CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    categories = crud.get_categories(db=db)
    return categories


@router.post("/", response_model=schemas.CategoryResponse, status_code=201, tags=["Categories"])
def create_category(data:schemas.CategoryCreate, db:Session = Depends(get_db)):
    if crud.get_category_by_name(db=db, name=data.name):
        raise HTTPException(status_code=409, detail="Category with this name already exists")
    category = crud.create_category(db=db, data=data)

    #return {"status": "ok", "message": "Category created successfully", "data": category}
    return category