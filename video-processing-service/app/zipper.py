import zipfile
import os

def zip_frames(input_dir, output_zip):
    with zipfile.ZipFile(output_zip, "w") as zipf:
        for root, _, files in os.walk(input_dir):
            for file in files:
                full_path = os.path.join(root, file)
                zipf.write(full_path, arcname=file)
