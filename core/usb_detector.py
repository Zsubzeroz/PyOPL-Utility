import os

def detect_usb_drives():
    """
    Procura dispositivos montados tipicamente usados para pendrives no Linux.
    Os ambientes Desktop (GNOME, KDE, XFCE, etc) montam automaticamente em:
    /media/<username>/<nome_pendrive>
    /run/media/<username>/<nome_pendrive>
    """
    username = os.getenv('USER') or os.getenv('LOGNAME') or os.getlogin()
    
    # Caminhos comuns de montagem automática
    search_paths = [
        f"/media/{username}",
        f"/run/media/{username}"
    ]
    
    found_drives = []
    
    for base_path in search_paths:
        if os.path.exists(base_path):
            for drive_name in os.listdir(base_path):
                drive_path = os.path.join(base_path, drive_name)
                if os.path.ismount(drive_path) or os.path.isdir(drive_path):
                    # Tenta pegar o tamanho livre e total para exibir
                    try:
                        statvfs = os.statvfs(drive_path)
                        total_size_gb = (statvfs.f_blocks * statvfs.f_frsize) / (1024**3)
                        free_size_gb = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)
                        
                        label = f"{drive_name} [{free_size_gb:.1f} GB livres de {total_size_gb:.1f} GB]"
                        found_drives.append({
                            "name": label,
                            "path": drive_path
                        })
                    except Exception:
                        found_drives.append({
                            "name": drive_name,
                            "path": drive_path
                        })
                        
    return found_drives
