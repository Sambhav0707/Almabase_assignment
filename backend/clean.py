import shutil
import os

folders = ["chroma_data", "uploads", "exports"]

for folder in folders:
    if os.path.exists(folder):
        try:
            shutil.rmtree(folder)
            print(f"Successfully deleted {folder}")
        except Exception as e:
            print(f"Failed to delete {folder}: {e}")
    else:
        print(f"{folder} does not exist.")
