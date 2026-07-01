#from app import models
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import categories
from app.database import Base, engine

@asynccontextmanager
async def lifespan(ap: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

#
app = FastAPI(
    title="Task Manager API",
    description="Task Manager API for managing tasks and categories",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(categories.router, prefix="/categories", tags=["Categories"])

@app.get("/", tags=["Health"])
def root():
    return { 
            "status": "ok", 
            "message": "Task Manager API is running" 
    }