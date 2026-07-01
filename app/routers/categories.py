from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


router = APIRouter()

@router.get("/", tags=["Categories"])
def list_categories():
    print("Listing categories")
    return {"status": "ok", "message": "Categories listed successfully"}