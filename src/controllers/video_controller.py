from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import shutil
import uuid
import os

from src.services.video_processor import VideoProcessor
from src.utils.zipper import create_zip

router = APIRouter()

UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    video_id = str(uuid.uuid4())
    video_path = f"{UPLOAD_FOLDER}{video_id}_{file.filename}"

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    processor = VideoProcessor(video_path, video_id)
    frames_folder = processor.extract_frames()

    zip_path = create_zip(frames_folder, video_id)

    if not zip_path:
        raise HTTPException(status_code=500, detail="Erro ao criar arquivo ZIP")

    return FileResponse(path=zip_path, filename=os.path.basename(zip_path), media_type='application/zip')