import cv2
import os

class VideoProcessor:
    def __init__(self, video_path: str, video_id: str):
        self.video_path = video_path
        self.output_folder = f"uploads/{video_id}_frames/"
        os.makedirs(self.output_folder, exist_ok=True)

    def extract_frames(self):
        cap = cv2.VideoCapture(self.video_path)

        success, frame = cap.read()
        count = 0

        while success:
            frame_path = os.path.join(self.output_folder, f"frame_{count}.jpg")
            cv2.imwrite(frame_path, frame)
            success, frame = cap.read()
            count += 1

        cap.release()
        return self.output_folder