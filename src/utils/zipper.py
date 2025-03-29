import zipfile
import os

def create_zip(folder_path: str, zip_name: str):
    zip_path = f"{folder_path.rstrip('/')}.zip"
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    zipf.write(
                        os.path.join(root, file),
                        arcname=os.path.relpath(os.path.join(root, file), folder_path)
                    )
        return zip_path
    except Exception as e:
        print(f"Erro ao criar ZIP: {e}")
        return None