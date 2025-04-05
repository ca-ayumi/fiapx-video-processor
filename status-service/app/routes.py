from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Video
from fastapi.responses import FileResponse
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/videos")
def list_videos(user_email: str, db: Session = Depends(get_db)):
    videos = db.query(Video).filter_by(user_email=user_email).all()
    return [
        {
            "filename": video.filename,
            "status": video.status,
            "download_url": f"/download/{video.filename.split('.')[0]}.zip"
            if video.status == "done" else None
        }
        for video in videos
    ]

@router.get("/download/{filename}")
def download_zip(filename: str):
    zip_path = f"/tmp/processed/{filename}"
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return FileResponse(zip_path, media_type='application/zip', filename=filename)
