import os
import pycdlib
import sys

def create_fake_ps2_iso(output_path: str, game_id: str):
    """
    Creates a fake ISO containing a dummy SYSTEM.CNF for testing.
    """
    iso = pycdlib.PyCdlib()
    iso.new(interchange_level=1)
    
    import io
    
    system_cnf_content = f"BOOT2 = cdrom0:\\{game_id};1\nVER = 1.00\nVMODE = NTSC\n"
    fp = io.BytesIO(system_cnf_content.encode('utf-8'))
    
    # pycdlib expects a file-like object in binary mode
    iso.add_fp(fp, len(system_cnf_content), '/SYSTEM.CNF;1')
    
    iso.write(output_path)
    iso.close()
    print(f"Created fake ISO at {output_path} with Game ID {game_id}")

if __name__ == "__main__":
    os.makedirs("test_data", exist_ok=True)
    fake_iso_path = "test_data/God_of_War.iso"
    
    # We can accept custom game id
    game_id = sys.argv[1] if len(sys.argv) > 1 else "SCUS_974.81"
    create_fake_ps2_iso(fake_iso_path, game_id)
