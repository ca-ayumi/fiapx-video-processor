from fastapi import FastAPI
from app.routes import router
from app.database import create_db

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def startup():
    create_db()