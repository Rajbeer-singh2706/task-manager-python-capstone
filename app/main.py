from app import models
from fastapi import FastAPI


app = FastAPI(
    title="",
    description="",
    version="",
    lifespan=None
)


@app.get("/", tags=["Health"])
def root():
    return { 
            "status": "ok", 
            "message": "Task Manager API is running" 
    }