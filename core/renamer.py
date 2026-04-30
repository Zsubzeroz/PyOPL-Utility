import os
import re

def rename_iso_for_opl(iso_path: str, game_id: str) -> str:
    """
    Renames the given ISO file to the OPL format: GAME_ID.Original_Name.iso
    If the name is already correctly formatted, does nothing.
    """
    directory = os.path.dirname(iso_path)
    original_filename = os.path.basename(iso_path)
    
    # Check if already formatted
    # e.g., SLUS_210.66.My Game.iso
    if original_filename.startswith(game_id + '.'):
        return iso_path
        
    # Remove any existing ID pattern from the filename just in case
    # Example: if someone named it [SLUS_210.66] Game.iso
    clean_name = re.sub(r'\[?' + re.escape(game_id) + r'\]?\s*-?\s*', '', original_filename, flags=re.IGNORECASE).strip()
    
    # Also strip any generic ID patterns like SLUS-123.45 if they exist but don't match
    clean_name = re.sub(r'^[A-Z]{4}[_-]\d{3}\.?\d{2}\s*[-_]?\s*', '', clean_name, flags=re.IGNORECASE).strip()
    
    # If it ends in .iso, remove it temporarily
    if clean_name.lower().endswith('.iso'):
        clean_name = clean_name[:-4].strip()
        
    new_filename = f"{game_id}.{clean_name}.iso"
    new_filepath = os.path.join(directory, new_filename)
    
    os.rename(iso_path, new_filepath)
    return new_filepath
