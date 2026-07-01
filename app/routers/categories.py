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

@router.get("/{category_id}", response_model=schemas.CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = crud.get_category(db, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    if not crud.delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")


@router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
    category_id: int,
    data:schemas.CategoryUpdate,
    db: Session = Depends(get_db)
):
    if data.name is not None:
        existing = crud.get_category_by_name(db,data.name)
        if existing and existing.id != category_id:
            raise HTTPException(status_code=409, detail="Category name already exists")
        cat = crud.update_category(db,category_id,data)
        if not cat:
            raise HTTPException(status_code=409, detail="Category name already exists")
        return cat