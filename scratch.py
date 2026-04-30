import re
from core.renamer import rename_iso_for_opl

def simulate(iso_path, game_id):
    original_filename = iso_path
    if original_filename.startswith(game_id + '.'):
        return iso_path
        
    clean_name = re.sub(r'\[?' + re.escape(game_id) + r'\]?\s*-?\s*', '', original_filename, flags=re.IGNORECASE).strip()
    clean_name = re.sub(r'^[A-Z]{4}[_-]\d{3}\.?\d{2}\s*[-_]?\s*', '', clean_name, flags=re.IGNORECASE).strip()
    
    if clean_name.lower().endswith('.iso'):
        clean_name = clean_name[:-4].strip()
        
    new_filename = f"{game_id}.{clean_name}.iso"
    return new_filename

print("1:", simulate("SLUS_205.00.iso", "SLUS_205.00"))
print("2:", simulate("SLUS-205.00.iso", "SLUS_205.00"))
print("3:", simulate("SLUS-20500.iso", "SLUS_205.00"))
print("4:", simulate("[SLUS_205.00] God of War.iso", "SLUS_205.00"))
print("5:", simulate("God of War.iso", "SLUS_205.00"))
print("6:", simulate("SLUS_205.00.God of War.iso", "SLUS_205.00"))
