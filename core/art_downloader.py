import os
import urllib.request
import urllib.error

def convert_opl_id_to_github_id(opl_id: str) -> str:
    """
    Converte o Game ID do OPL (ex: SLUS_210.66) para o formato usado 
    no repositório ps2-covers (ex: SLUS-21066).
    """
    # Se já vier sem o sublinhado, tentamos apenas remover o ponto
    if "_" in opl_id:
        parts = opl_id.split("_")
        prefix = parts[0]
        number = parts[1].replace(".", "")
        return f"{prefix}-{number}"
    
    return opl_id.replace(".", "").replace("_", "-")

def download_arts(iso_files_list, usb_root: str, progress_callback=None):
    """
    Baixa as capas dos jogos contidos na lista `iso_files_list`.
    iso_files_list deve ser uma lista de dicionários contendo a chave 'game_id'.
    """
    art_folder = os.path.join(usb_root, "ART")
    
    # Cria a pasta ART se ela não existir
    if not os.path.exists(art_folder):
        os.makedirs(art_folder)
        
    total_games = len(iso_files_list)
    success_count = 0
    error_count = 0
    
    for i, data in enumerate(iso_files_list):
        game_id = data.get("game_id", "N/A")
        
        if game_id == "N/A":
            error_count += 1
            if progress_callback:
                progress_callback(i + 1, total_games, "Ignorado (Sem Game ID)")
            continue
            
        github_id = convert_opl_id_to_github_id(game_id)
        
        # URL do repositório xlenore (rápido e completo)
        cover_url = f"https://raw.githubusercontent.com/xlenore/ps2-covers/main/covers/default/{github_id}.jpg"
        
        # Nome padrão OPL para capas: GAME_ID_COV.jpg
        # OPL aceita JPG ou PNG. O xlenore usa jpg.
        dest_filename = f"{game_id}_COV.jpg"
        dest_path = os.path.join(art_folder, dest_filename)
        
        # Se a capa já existe, pulamos para economizar banda
        if os.path.exists(dest_path):
            success_count += 1
            if progress_callback:
                progress_callback(i + 1, total_games, f"{game_id} (Já existe)")
            continue
            
        try:
            req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response, open(dest_path, 'wb') as out_file:
                data_img = response.read()
                out_file.write(data_img)
            success_count += 1
            status_msg = f"{game_id} (Sucesso)"
        except urllib.error.HTTPError as e:
            error_count += 1
            status_msg = f"{game_id} (Não encontrada)"
        except Exception as e:
            error_count += 1
            status_msg = f"{game_id} (Erro de rede)"
            
        if progress_callback:
            progress_callback(i + 1, total_games, status_msg)
            
    return success_count, error_count
