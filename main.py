from fastapi import FastAPI
from src.controllers.video_controller import router as video_router

app = FastAPI(title="FIAP X Video Processor")

app.include_router(video_router, prefix="/videos")