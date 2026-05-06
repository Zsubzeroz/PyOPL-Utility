import os
import re

def rename_iso_for_opl(iso_path: str, game_id: str, custom_name: str = None) -> str:
    """
    Renames the given ISO file to the OPL format: GAME_ID.Original_Name.iso
    If custom_name is provided, it uses that instead of extracting from original_filename.
    """
    directory = os.path.dirname(iso_path)
    original_filename = os.path.basename(iso_path)
    
    if custom_name and custom_name.strip():
        clean_name = custom_name.strip()
        # If the user typed .iso by mistake, remove it
        if clean_name.lower().endswith('.iso'):
            clean_name = clean_name[:-4].strip()
    else:
        # Check if already formatted
        # e.g., SLUS_210.66.My Game.iso
        if original_filename.startswith(game_id + '.'):
            return iso_path
            
        clean_name = original_filename
        
        # Remove any existing ID pattern from the filename just in case
        clean_name = re.sub(r'\[?' + re.escape(game_id) + r'\]?\s*-?\s*', '', clean_name, flags=re.IGNORECASE).strip()
        
        # Also strip any generic ID patterns like SLUS-123.45 if they exist but don't match
        clean_name = re.sub(r'^[A-Z]{4}[_-]\d{3}\.?\d{2}\s*[-_]?\s*', '', clean_name, flags=re.IGNORECASE).strip()
        
        # If it ends in .iso, remove it temporarily
        if clean_name.lower().endswith('.iso'):
            clean_name = clean_name[:-4].strip()
            
    if clean_name:
        new_filename = f"{game_id}.{clean_name}.iso"
    else:
        new_filename = f"{game_id}.iso"
        
    new_filepath = os.path.join(directory, new_filename)
    
    if iso_path != new_filepath:
        os.rename(iso_path, new_filepath)
        
    return new_filepath
