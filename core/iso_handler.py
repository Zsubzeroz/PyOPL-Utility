import pycdlib
import io
import re

def get_game_id_from_iso(iso_path: str) -> str:
    """
    Extracts the Game ID from the SYSTEM.CNF file inside the given PS2 ISO.
    Returns the Game ID in OPL format (e.g., SLUS_210.66) or None if not found.
    """
    iso = pycdlib.PyCdlib()
    try:
        iso.open(iso_path)
        
        # In ISO9660, files often end with ;1 for versioning
        # We need to find SYSTEM.CNF
        cnf_path = None
        for dirname, dirlist, filelist in iso.walk(iso_path='/'):
            if dirname == '/':
                for f in filelist:
                    # File names might have ;1 appended
                    if f.startswith('SYSTEM.CNF'):
                        cnf_path = f'/{f}'
                        break
                break

        if not cnf_path:
            return None

        # Read the file
        extracted = io.BytesIO()
        iso.get_file_from_iso_fp(extracted, iso_path=cnf_path)
        content = extracted.getvalue().decode('utf-8', errors='ignore')
        
        return parse_system_cnf(content)

    except Exception as e:
        print(f"Error reading ISO {iso_path}: {e}")
        return None
    finally:
        iso.close()

def parse_system_cnf(content: str) -> str:
    """
    Parses the SYSTEM.CNF content to extract the Game ID.
    Usually found in a line like: BOOT2 = cdrom0:\\SLUS_210.66;1
    """
    for line in content.splitlines():
        if line.strip().startswith('BOOT2'):
            # Example: BOOT2 = cdrom0:\SLUS_210.66;1
            match = re.search(r'\\([A-Z0-9]{4}_[0-9]{3}\.[0-9]{2})', line, re.IGNORECASE)
            if match:
                game_id = match.group(1).upper()
                return game_id
    return None
