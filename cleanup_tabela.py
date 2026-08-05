import os
from pathlib import Path

def cleanup_generated_files():
    data_dir = Path("market_data")
    count = 0
    for json_file in data_dir.rglob("*.json"):
        # delete json file
        os.remove(json_file)
        count += 1
    
    # Also delete daily reports txt
    for txt_file in (data_dir / "daily_reports").rglob("*.txt"):
        os.remove(txt_file)

    print(f"Removed {count} JSON files (including registry).")

if __name__ == "__main__":
    cleanup_generated_files()
