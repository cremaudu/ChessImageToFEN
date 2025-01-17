import os
import platform
import zipfile
import shutil
import logging
import requests
from pathlib import Path
import subprocess
import stat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STOCKFISH_VERSIONS = {
    'windows': {
        'x64': 'https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-windows-x86-64.zip',
        'x86': 'https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-windows-x86-32.zip'
    },
    'linux': {
        'x64': 'https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-ubuntu-x86-64.zip',
        'x86': 'https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-linux-x86-32.zip'
    },
    'darwin': {  # macOS
        'x64': 'https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-macos-x86-64.zip',
        'arm64': 'https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-macos-arm64.zip'
    }
}

def get_system_info():
    """Détermine le système d'exploitation et l'architecture"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Détermine l'architecture
    if system == 'windows' or system == 'linux':
        arch = 'x64' if machine in ['x86_64', 'amd64'] else 'x86'
    elif system == 'darwin':  # macOS
        arch = 'arm64' if machine == 'arm64' else 'x64'
    else:
        raise ValueError(f"Système d'exploitation non supporté : {system}")
    
    return system, arch

def download_file(url: str, target_path: Path):
    """Télécharge un fichier avec une barre de progression"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0
        
        logger.info(f"Téléchargement de {url}")
        logger.info(f"Taille totale : {total_size / (1024*1024):.1f} MB")
        
        with open(target_path, 'wb') as f:
            for data in response.iter_content(block_size):
                downloaded += len(data)
                f.write(data)
                
                # Affiche la progression
                progress = downloaded / total_size * 100
                logger.info(f"Progression : {progress:.1f}%")
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement : {str(e)}")
        return False

def extract_zip(zip_path: Path, extract_path: Path):
    """Extrait un fichier ZIP"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction : {str(e)}")
        return False

def make_executable(file_path: Path):
    """Rend un fichier exécutable (Linux/macOS)"""
    try:
        current = os.stat(file_path)
        os.chmod(file_path, current.st_mode | stat.S_IEXEC)
        return True
    except Exception as e:
        logger.error(f"Erreur lors du changement des permissions : {str(e)}")
        return False

def test_stockfish(stockfish_path: Path):
    """Teste l'installation de Stockfish"""
    try:
        # Lance Stockfish avec l'option version
        result = subprocess.run(
            [str(stockfish_path)],
            input=b"uci\nquit\n",
            capture_output=True,
            timeout=5
        )
        
        # Vérifie la sortie
        output = result.stdout.decode('utf-8')
        if 'Stockfish' in output and 'id author' in output:
            logger.info("Test Stockfish réussi !")
            return True
        else:
            logger.error("La sortie de Stockfish n'est pas celle attendue")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout lors du test de Stockfish")
        return False
    except Exception as e:
        logger.error(f"Erreur lors du test de Stockfish : {str(e)}")
        return False

def setup_stockfish():
    """Configure Stockfish pour le projet"""
    try:
        # Détermine le système et l'architecture
        system, arch = get_system_info()
        logger.info(f"Système détecté : {system} ({arch})")
        
        # Vérifie si l'URL existe pour cette configuration
        if system not in STOCKFISH_VERSIONS or arch not in STOCKFISH_VERSIONS[system]:
            raise ValueError(f"Pas de version Stockfish pour {system} ({arch})")
        
        # Crée les dossiers nécessaires
        engines_dir = Path('engines/stockfish')
        engines_dir.mkdir(parents=True, exist_ok=True)
        
        # Détermine les chemins
        zip_path = engines_dir / 'stockfish.zip'
        stockfish_url = STOCKFISH_VERSIONS[system][arch]
        
        # Nom du fichier Stockfish selon le système
        if system == 'windows':
            stockfish_name = 'stockfish-windows-x86-64.exe' if arch == 'x64' else 'stockfish-windows-x86-32.exe'
        else:
            stockfish_name = f'stockfish-{system}-{arch}'
        
        stockfish_path = engines_dir / stockfish_name
        
        # Télécharge Stockfish si nécessaire
        if not stockfish_path.exists():
            logger.info("Téléchargement de Stockfish...")
            if not download_file(stockfish_url, zip_path):
                raise Exception("Échec du téléchargement")
            
            # Extrait le ZIP
            logger.info("Extraction de Stockfish...")
            if not extract_zip(zip_path, engines_dir):
                raise Exception("Échec de l'extraction")
            
            # Supprime le ZIP
            zip_path.unlink()
            
            # Rend le fichier exécutable sur Unix
            if system != 'windows':
                logger.info("Configuration des permissions...")
                if not make_executable(stockfish_path):
                    raise Exception("Échec de la configuration des permissions")
        
        # Teste Stockfish
        logger.info("Test de Stockfish...")
        if not test_stockfish(stockfish_path):
            raise Exception("Échec du test de Stockfish")
        
        logger.info(f"Stockfish installé avec succès dans {stockfish_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la configuration de Stockfish : {str(e)}")
        return False

if __name__ == '__main__':
    setup_stockfish()
