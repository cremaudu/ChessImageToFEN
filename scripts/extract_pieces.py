import cv2
import numpy as np
import os
from pathlib import Path

def read_image(image_path):
    # Lire le fichier en mode binaire
    with open(image_path, 'rb') as f:
        img_array = np.frombuffer(f.read(), np.uint8)
    
    # Décoder l'image
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Impossible de lire l'image")
    return img

def create_piece_directories():
    # Créer les répertoires pour chaque type de pièce
    base_dir = Path("data/pieces_new")
    piece_types = ['P', 'R', 'N', 'B', 'Q', 'K', 'empty']
    
    for piece in piece_types:
        piece_dir = base_dir / piece
        piece_dir.mkdir(parents=True, exist_ok=True)

def extract_squares(image_path):
    # Lire l'image
    img = read_image(image_path)
    
    # Obtenir les dimensions de l'image
    height, width = img.shape[:2]
    
    # Calculer la taille d'une case
    square_size = height // 8
    
    # Dictionnaire pour stocker les positions initiales des pièces
    initial_positions = {
        'R': [(0,0), (0,7), (7,0), (7,7)],  # Tours
        'N': [(0,1), (0,6), (7,1), (7,6)],  # Cavaliers
        'B': [(0,2), (0,5), (7,2), (7,5)],  # Fous
        'Q': [(0,3), (7,3)],                 # Dames
        'K': [(0,4), (7,4)],                 # Rois
        'P': [(1,i) for i in range(8)] + [(6,i) for i in range(8)],  # Pions
        'empty': [(i,j) for i in range(2,6) for j in range(8)]  # Cases vides
    }
    
    # Extraire et sauvegarder chaque type de pièce
    for piece_type, positions in initial_positions.items():
        for idx, (row, col) in enumerate(positions):
            # Extraire la case
            y = row * square_size
            x = col * square_size
            square = img[y:y+square_size, x:x+square_size]
            
            # Sauvegarder l'image
            output_path = f"data/pieces_new/{piece_type}/{piece_type}_{idx}.png"
            # Encoder l'image en PNG
            is_success, buffer = cv2.imencode(".png", square)
            if is_success:
                # Écrire le buffer dans un fichier
                with open(output_path, "wb") as f:
                    f.write(buffer)
                print(f"Sauvegarde de {output_path}")
            else:
                print(f"Erreur lors de la sauvegarde de {output_path}")

def main():
    # Créer les répertoires nécessaires
    create_piece_directories()
    
    # Chemin vers l'image de l'échiquier initial
    board_image = "data/reference_board.png"
    
    # Extraire les pièces
    try:
        extract_squares(board_image)
        print("Extraction des pièces terminée avec succès!")
    except Exception as e:
        print(f"Erreur lors de l'extraction : {str(e)}")

if __name__ == "__main__":
    main()
