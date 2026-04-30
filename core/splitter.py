import os
import struct
import binascii

CHUNK_SIZE = 1073741824  # Exatamente 1GB em bytes

def create_ul_cfg_entry(game_id: str, name: str, parts: int, is_cd: bool) -> bytes:
    """
    Cria uma entrada de 64 bytes para o arquivo ul.cfg do OPL.
    Estrutura:
    15 bytes: Game ID (ASCII, null padded)
    32 bytes: Game Name (ASCII, null padded)
    1 byte: Número de partes
    1 byte: Tipo de mídia (0x12 para CD, 0x14 para DVD)
    15 bytes: Padding (zeros)
    """
    # Assegura que a string caiba nos limites
    game_id_bytes = game_id.encode('ascii', errors='ignore')[:14]
    name_bytes = name.encode('ascii', errors='ignore')[:31]
    
    media_byte = 0x12 if is_cd else 0x14
    
    # <15s32sBB15x: little-endian, 15 char[], 32 char[], unsigned char, unsigned char, 15 pad bytes
    return struct.pack('<15s32sBB15x', game_id_bytes, name_bytes, parts, media_byte)

def update_ul_cfg(usb_root: str, game_id: str, name: str, parts: int, is_cd: bool = False):
    """
    Atualiza (ou cria) o arquivo ul.cfg na raiz do pendrive.
    """
    cfg_path = os.path.join(usb_root, 'ul.cfg')
    entry = create_ul_cfg_entry(game_id, name, parts, is_cd)
    
    entries = []
    # Se o arquivo já existe, lê todas as entradas
    if os.path.exists(cfg_path):
        with open(cfg_path, 'rb') as f:
            while True:
                chunk = f.read(64)
                if len(chunk) < 64:
                    break
                # Decodifica os primeiros 15 bytes para checar o ID
                existing_id = chunk[:15].decode('ascii', errors='ignore').strip('\x00')
                
                # Se o ID for diferente do que estamos gravando, mantém ele
                if existing_id != game_id:
                    entries.append(chunk)
                    
    # Adiciona a entrada nova
    entries.append(entry)
    
    # Regrava tudo
    with open(cfg_path, 'wb') as f:
        for e in entries:
            f.write(e)

def split_iso(iso_path: str, usb_root: str, game_id: str, name: str, progress_callback=None):
    """
    Divide a ISO em pedaços de 1GB e grava o arquivo ul.cfg.
    """
    file_size = os.path.getsize(iso_path)
    total_parts = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
    
    # Geramos um pseudo-CRC32 único baseado no nome para a nomenclatura do USBExtreme
    crc = binascii.crc32(name.encode('utf-8')) & 0xFFFFFFFF
    crc_hex = f"{crc:08X}"
    
    bytes_copied = 0
    
    with open(iso_path, 'rb') as f_in:
        for i in range(total_parts):
            # Ex: ul.8AA266C1.SLUS_210.66.00
            part_name = f"ul.{crc_hex}.{game_id}.{i:02d}"
            part_path = os.path.join(usb_root, part_name)
            
            with open(part_path, 'wb') as f_out:
                # Anti-fragmentation: pre-allocate space
                try:
                    part_size = min(CHUNK_SIZE, file_size - (i * CHUNK_SIZE))
                    os.posix_fallocate(f_out.fileno(), 0, part_size)
                except (AttributeError, OSError):
                    pass # Windows or unsupported filesystem
                    
                bytes_to_copy = CHUNK_SIZE
                while bytes_to_copy > 0:
                    read_size = min(bytes_to_copy, 1024 * 1024 * 10)  # Lemos de 10 em 10MB
                    chunk = f_in.read(read_size)
                    if not chunk:
                        break
                    f_out.write(chunk)
                    f_out.flush()
                    os.fsync(f_out.fileno())  # <--- Isso força o kernel a escrever no USB
                    
                    bytes_to_copy -= len(chunk)
                    bytes_copied += len(chunk)
                    
                    if progress_callback:
                        progress_callback(bytes_copied, file_size)
                        
    # Finalizou, atualiza o cfg. ISOs menores que 700MB consideramos CD.
    is_cd = file_size < (700 * 1024 * 1024)
    update_ul_cfg(usb_root, game_id, name, total_parts, is_cd)

def copy_iso_intact(iso_path: str, usb_root: str, game_id: str, name: str, progress_callback=None):
    """
    Copia uma ISO inteira (<4GB) para a pasta DVD ou CD no pendrive.
    Aplica fallocate para evitar fragmentação.
    """
    file_size = os.path.getsize(iso_path)
    
    # Menor que 700MB vai para pasta CD, senao DVD
    folder_name = "CD" if file_size < (700 * 1024 * 1024) else "DVD"
    target_dir = os.path.join(usb_root, folder_name)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    # OPL Format: GAME_ID.Name.iso
    # Se nao tiver name, usa só GAME_ID.iso
    if name:
        dest_filename = f"{game_id}.{name}.iso"
    else:
        dest_filename = f"{game_id}.iso"
        
    dest_path = os.path.join(target_dir, dest_filename)
    
    bytes_copied = 0
    with open(iso_path, 'rb') as f_in:
        with open(dest_path, 'wb') as f_out:
            # Anti-fragmentation: pre-allocate space
            try:
                os.posix_fallocate(f_out.fileno(), 0, file_size)
            except (AttributeError, OSError):
                pass
                
            while True:
                chunk = f_in.read(1024 * 1024 * 10) # 10MB
                if not chunk:
                    break
                f_out.write(chunk)
                f_out.flush()
                os.fsync(f_out.fileno())
                
                bytes_copied += len(chunk)
                if progress_callback:
                    progress_callback(bytes_copied, file_size)
