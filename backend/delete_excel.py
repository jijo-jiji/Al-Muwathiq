
import os
import glob

# Paths to clean
FOLDERS_TO_CLEAN = [
    os.path.join(os.path.dirname(__file__), "../data_source/BNM/data_bnm"),
    os.path.join(os.path.dirname(__file__), "../for_friend/data_bnm")
]

def delete_excel_files():
    print("🧹 Starting Excel Cleanup...")
    deleted_count = 0
    
    for folder in FOLDERS_TO_CLEAN:
        if not os.path.exists(folder):
            print(f"⚠️ Folder not found: {folder}")
            continue
            
        # Find all Excel files
        excel_files = glob.glob(os.path.join(folder, "*.xls")) + \
                      glob.glob(os.path.join(folder, "*.xlsx"))
        
        for file_path in excel_files:
            try:
                os.remove(file_path)
                print(f"❌ Deleted: {os.path.basename(file_path)}")
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ Failed to delete {os.path.basename(file_path)}: {e}")

    print(f"\n✨ Cleanup Complete. Removed {deleted_count} Excel files.")

if __name__ == "__main__":
    delete_excel_files()
