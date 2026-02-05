import os
from datetime import datetime
import shutil

def archive_image(image_path):
    date_folder = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(f"archive/{date_folder}", exist_ok=True)
    shutil.move(image_path, f"archive/{date_folder}/latest.jpg")
