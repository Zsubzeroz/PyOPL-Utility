import argparse
import os
import sys
from core.iso_handler import get_game_id_from_iso
from core.renamer import rename_iso_for_opl

def process_file(filepath: str):
    if not filepath.lower().endswith('.iso'):
        return
        
    print(f"Processing: {filepath}")
    game_id = get_game_id_from_iso(filepath)
    
    if not game_id:
        print(f"[-] Could not extract Game ID from {filepath}")
        return
        
    print(f"[+] Found Game ID: {game_id}")
    try:
        new_path = rename_iso_for_opl(filepath, game_id)
        if new_path != filepath:
            print(f"[+] Renamed to: {os.path.basename(new_path)}")
        else:
            print(f"[=] Already correctly named: {os.path.basename(new_path)}")
    except Exception as e:
        print(f"[-] Error renaming {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description="PyOPL Utility - Metadata Extraction and Renaming")
    parser.add_argument("path", help="Path to a PS2 ISO file or a directory containing ISOs")
    
    args = parser.parse_args()
    
    if os.path.isfile(args.path):
        process_file(args.path)
    elif os.path.isdir(args.path):
        print(f"Scanning directory: {args.path}")
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.lower().endswith('.iso'):
                    full_path = os.path.join(root, file)
                    process_file(full_path)
    else:
        print(f"Error: Path does not exist -> {args.path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
