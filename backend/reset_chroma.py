
import os
import shutil

DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

def reset_db():
    if os.path.exists(DB_PATH):
        print(f"🗑️ Deleting existing brain at: {DB_PATH}")
        shutil.rmtree(DB_PATH)
        print("✅ Deleted. You can now run ingest.py for a fresh start.")
    else:
        print("🤷 Brain not found (nothing to delete).")

if __name__ == "__main__":
    confirm = input("Are you sure you want to delete the brain? (y/n): ")
    if confirm.lower() == 'y':
        reset_db()
    else:
        print("✖️ Cancelled.")
