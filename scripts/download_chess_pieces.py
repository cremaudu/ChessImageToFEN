import os
import requests
import logging
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = "data"

def download_image(url, save_path):
    """Télécharge une image depuis une URL"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Image téléchargée : {save_path}")
            return True
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de {url}: {str(e)}")
    return False

def create_variations(img_path, save_dir, piece_name, num_variations=10):
    """Crée des variations d'une image avec différentes transformations"""
    try:
        img = Image.open(img_path)
        
        # Pour chaque variation
        for i in range(num_variations):
            # Rotation aléatoire légère (-15 à +15 degrés)
            angle = np.random.uniform(-15, 15)
            rotated = img.rotate(angle, resample=Image.Resampling.BILINEAR, expand=False)
            
            # Ajustement de la luminosité (80% à 120%)
            brightness = np.random.uniform(0.8, 1.2)
            brightened = Image.fromarray((np.array(rotated) * brightness).clip(0, 255).astype(np.uint8))
            
            # Léger zoom (90% à 110%)
            zoom = np.random.uniform(0.9, 1.1)
            w, h = brightened.size
            new_w, new_h = int(w * zoom), int(h * zoom)
            zoomed = brightened.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Recadre au centre si nécessaire
            if zoom > 1:
                left = (new_w - w) // 2
                top = (new_h - h) // 2
                zoomed = zoomed.crop((left, top, left + w, top + h))
            else:
                # Ajoute des bordures noires si zoom < 1
                final = Image.new('RGB', (w, h), (0, 0, 0))
                left = (w - new_w) // 2
                top = (h - new_h) // 2
                final.paste(zoomed, (left, top))
                zoomed = final
            
            # Sauvegarde la variation
            save_path = os.path.join(save_dir, f"{piece_name}_var_{i}.png")
            zoomed.save(save_path)
            logger.info(f"Variation créée : {save_path}")
            
    except Exception as e:
        logger.error(f"Erreur lors de la création des variations pour {img_path}: {str(e)}")

def download_chess_com_pieces():
    """Télécharge les pièces depuis chess.com et crée des variations"""
    # URL de base pour les pièces de chess.com (différents thèmes)
    themes = {
        'neo': 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/',
        'classic': 'https://images.chesscomfiles.com/chess-themes/pieces/classic/150/',
        'glass': 'https://images.chesscomfiles.com/chess-themes/pieces/glass/150/'
    }
    
    pieces = {
        'P': 'wp.png',  # Pion blanc
        'N': 'wn.png',  # Cavalier blanc
        'B': 'wb.png',  # Fou blanc
        'R': 'wr.png',  # Tour blanche
        'Q': 'wq.png',  # Dame blanche
        'K': 'wk.png',  # Roi blanc
        'p': 'bp.png',  # Pion noir
        'n': 'bn.png',  # Cavalier noir
        'b': 'bb.png',  # Fou noir
        'r': 'br.png',  # Tour noire
        'q': 'bq.png',  # Dame noire
        'k': 'bk.png'   # Roi noir
    }
    
    for theme_name, base_url in themes.items():
        for piece, filename in pieces.items():
            url = base_url + filename
            save_dir = os.path.join(DATA_DIR, "pieces", piece.upper())
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f"{theme_name}_{filename}")
            
            if download_image(url, save_path):
                # Crée des variations pour chaque image téléchargée
                create_variations(save_path, save_dir, f"{theme_name}_{piece}")

    # URLs des pièces d'échecs
    PIECE_URLS = {
        'B': [
            'https://www.chess.com/chess-themes/pieces/neo/150/bb.png',
            'https://www.chess.com/chess-themes/pieces/classic/150/bb.png',
            'https://www.chess.com/chess-themes/pieces/wood/150/bb.png',
            'https://www.chess.com/chess-themes/pieces/marble/150/bb.png',
            'https://www.chess.com/chess-themes/pieces/metal/150/bb.png',
            'https://www.chess.com/chess-themes/pieces/bases/150/bb.png',
            'https://www.chess.com/chess-themes/pieces/tournament/150/bb.png',
            'https://www.chess.com/chess-themes/pieces/vintage/150/bb.png'
        ],
        'K': ['https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bk.png'],
        'N': ['https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bn.png'],
        'P': ['https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bp.png'],
        'Q': ['https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bq.png'],
        'R': ['https://images.chesscomfiles.com/chess-themes/pieces/neo/150/br.png']
    }

    for piece, urls in PIECE_URLS.items():
        piece_dir = os.path.join(DATA_DIR, 'pieces', piece)
        os.makedirs(piece_dir, exist_ok=True)
        
        for i, url in enumerate(urls):
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                # Sauvegarder l'image originale
                img_path = os.path.join(piece_dir, f'{piece}_{i}.png')
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                
                # Pour les fous, créer des variations supplémentaires
                if piece == 'B':
                    try:
                        img = Image.open(img_path).convert('RGBA')
                        
                        # Plus de rotations
                        for angle in [-20, -15, -10, -5, 5, 10, 15, 20]:
                            rotated = img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
                            rotated.save(os.path.join(piece_dir, f'{piece}_{i}_rot{angle}.png'))
                        
                        # Plus de variations d'échelle
                        for scale in [0.7, 0.8, 0.9, 1.1, 1.2, 1.3]:
                            new_size = (int(img.width * scale), int(img.height * scale))
                            resized = img.resize(new_size, Image.Resampling.LANCZOS)
                            resized.save(os.path.join(piece_dir, f'{piece}_{i}_scale{scale}.png'))
                        
                        # Plus de variations de luminosité
                        enhancer = ImageEnhance.Brightness(img)
                        for factor in [0.7, 0.8, 0.9, 1.1, 1.2, 1.3]:
                            enhanced = enhancer.enhance(factor)
                            enhanced.save(os.path.join(piece_dir, f'{piece}_{i}_bright{factor}.png'))
                        
                        # Plus de variations de contraste
                        enhancer = ImageEnhance.Contrast(img)
                        for factor in [0.7, 0.8, 0.9, 1.1, 1.2, 1.3]:
                            enhanced = enhancer.enhance(factor)
                            enhanced.save(os.path.join(piece_dir, f'{piece}_{i}_contrast{factor}.png'))
                        
                        # Ajout de flou gaussien léger
                        for radius in [0.5, 1.0, 1.5]:
                            blurred = img.filter(ImageFilter.GaussianBlur(radius))
                            blurred.save(os.path.join(piece_dir, f'{piece}_{i}_blur{radius}.png'))
                        
                        # Créer des variations avec différentes teintes
                        for hue_shift in [-30, -20, -10, 10, 20, 30]:
                            hsv = img.convert('HSV')
                            h, s, v = hsv.split()
                            h = h.point(lambda x: (x + hue_shift) % 256)
                            shifted = Image.merge('HSV', (h, s, v)).convert('RGBA')
                            shifted.save(os.path.join(piece_dir, f'{piece}_{i}_hue{hue_shift}.png'))
                        
                    except Exception as e:
                        logger.error(f'Erreur lors de la création des variations pour {img_path}: {str(e)}')
                
                logger.info(f'Téléchargé : {piece}_{i}.png')
            except Exception as e:
                logger.error(f'Erreur lors du téléchargement de {url}: {str(e)}')

def create_empty_squares():
    """Crée des cases vides avec variations"""
    empty_dir = os.path.join(DATA_DIR, "pieces", "empty")
    os.makedirs(empty_dir, exist_ok=True)
    
    # Couleurs de base pour les cases
    colors = {
        'white': (240, 240, 240),
        'black': (181, 181, 181),
        'white_alt': (255, 255, 255),
        'black_alt': (140, 140, 140)
    }
    
    # Crée plusieurs variations de cases vides
    for color_name, color in colors.items():
        img = Image.new('RGB', (100, 100), color)
        save_path = os.path.join(empty_dir, f"{color_name}_square.png")
        img.save(save_path)
        
        # Crée des variations avec différentes luminosités
        create_variations(save_path, empty_dir, color_name)

def main():
    """Fonction principale"""
    # Crée le dossier de base s'il n'existe pas
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Télécharge les pièces de chess.com et crée des variations
    logger.info("Téléchargement des pièces depuis chess.com...")
    download_chess_com_pieces()
    
    # Crée les cases vides avec variations
    logger.info("Création des cases vides...")
    create_empty_squares()

if __name__ == "__main__":
    main()
