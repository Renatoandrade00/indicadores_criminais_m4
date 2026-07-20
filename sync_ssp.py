import os
import json
import requests
import gdown
from datetime import datetime
import etl

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.environ.get("GOOGLE_API_KEY")
DRIVE_FOLDER_ID = "1lyWzon95y_a4H6dmexFT4Vd1GidXxBtD"
MANIFEST_PATH = os.path.join("data", "sync_manifest.json")
RAW_DRIVE_DIR = os.path.join("data", "raw_drive")

def list_drive_files(folder_id, api_key):
    """
    Lista recursivamente arquivos do Google Drive usando API v3.
    Retorna uma lista de dicionários com os detalhes dos arquivos.
    """
    url = "https://www.googleapis.com/drive/v3/files"
    files = []
    
    # Fila para explorar subpastas: (folder_id, folder_name)
    queue = [(folder_id, "")]
    
    while queue:
        current_id, current_path = queue.pop(0)
        
        params = {
            'q': f"'{current_id}' in parents and trashed=false",
            'key': api_key,
            'fields': 'nextPageToken, files(id, name, mimeType)',
            'pageSize': 1000
        }
        
        while True:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('files', []):
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    # Adiciona subpasta na fila
                    subpath = os.path.join(current_path, item['name']) if current_path else item['name']
                    queue.append((item['id'], subpath))
                else:
                    item['folder'] = current_path
                    files.append(item)
                    
            if 'nextPageToken' in data:
                params['pageToken'] = data['nextPageToken']
            else:
                break
                
    return files

def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar manifest: {e}")
    
    return {
        "last_sync": "1970-01-01T00:00:00Z",
        "files": {}
    }

def save_manifest(manifest):
    # Garantir que a pasta existe
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    manifest['last_sync'] = datetime.utcnow().isoformat() + "Z"
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

def main():
    if not API_KEY:
        print("Erro: GOOGLE_API_KEY não está definida.")
        return
        
    print("Iniciando sincronização com SSP-SP Google Drive...")
    try:
        remote_files = list_drive_files(DRIVE_FOLDER_ID, API_KEY)
    except Exception as e:
        print(f"Erro ao acessar API do Google Drive: {e}")
        return
        
    manifest = load_manifest()
    
    new_files_count = 0
    
    for r_file in remote_files:
        file_id = r_file['id']
        file_name = r_file['name']
        folder_name = r_file['folder']
        
        if file_id not in manifest['files']:
            print(f"Novo arquivo detectado: [{folder_name}] {file_name}")
            
            # Criar pasta local se não existir
            dest_dir = os.path.join(RAW_DRIVE_DIR, folder_name)
            os.makedirs(dest_dir, exist_ok=True)
            
            dest_path = os.path.join(dest_dir, file_name)
            
            # Baixar com gdown
            download_url = f'https://drive.google.com/uc?id={file_id}'
            try:
                # Retorna None se falhar. quiet=False por agora para logs
                gdown.download(download_url, dest_path, quiet=True)
                
                if os.path.exists(dest_path):
                    # Registrar no manifest
                    manifest['files'][file_id] = {
                        "name": file_name,
                        "folder": folder_name,
                        "downloaded_at": datetime.utcnow().isoformat() + "Z"
                    }
                    new_files_count += 1
                else:
                    print(f"Arquivo não foi salvo no destino esperado: {dest_path}")
            except Exception as e:
                print(f"Erro ao baixar {file_name}: {e}")
                
    if new_files_count > 0:
        print(f"\nForam baixados {new_files_count} novos arquivos.")
        print("Executando pipeline ETL...")
        save_manifest(manifest)
        try:
            etl.run_etl()
            print("ETL concluído com sucesso.")
        except Exception as e:
            print(f"Erro durante execução do ETL: {e}")
    else:
        print("Nenhum arquivo novo para baixar. Base está atualizada.")
        save_manifest(manifest)

if __name__ == "__main__":
    main()
