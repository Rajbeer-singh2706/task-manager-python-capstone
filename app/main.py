#from app import models
from fastapi import FastAPI
from app.routers import categories

#
app = FastAPI(
    title="Task Manager API",
    description="Task Manager API for managing tasks and categories",
    version="0.1.0",
    lifespan=None,
)

app.include_router(categories.router, prefix="/categories", tags=["Categories"])

@app.get("/", tags=["Health"])
def root():
    return { 
            "status": "ok", 
            "message": "Task Manager API is running" 
    }