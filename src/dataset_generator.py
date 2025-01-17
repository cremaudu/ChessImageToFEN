import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from typing import Tuple, Optional

class DatasetGenerator:
    # Mapping des pièces aux caractères ASCII
    PIECES = {
        'K': 'K', 'Q': 'Q', 'R': 'R', 'B': 'B', 'N': 'N', 'P': 'P',  # Pièces blanches
        'k': 'k', 'q': 'q', 'r': 'r', 'b': 'b', 'n': 'n', 'p': 'p'   # Pièces noires
    }
    
    def __init__(self, output_dir: str = 'data/pieces'):
        """
        Initialise le générateur de dataset.
        
        Args:
            output_dir: Répertoire de sortie pour les images générées
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Crée un sous-dossier pour chaque type de pièce
        for piece in list(self.PIECES.keys()) + ['empty']:
            os.makedirs(os.path.join(output_dir, piece), exist_ok=True)
    
    def _create_random_background(self, size: Tuple[int, int]) -> Image.Image:
        """Crée un fond d'échiquier aléatoire"""
        # Couleurs de l'échiquier
        light = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
        dark = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        
        img = Image.new('RGB', size)
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, size[0], size[1]], fill=light if random.random() > 0.5 else dark)
        return img
    
    def _add_noise(self, img: Image.Image, intensity: float = 0.1) -> Image.Image:
        """Ajoute du bruit à l'image"""
        img_array = np.array(img)
        noise = np.random.normal(0, intensity * 255, img_array.shape)
        noisy_img = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_img)
    
    def _apply_random_transform(self, img: Image.Image) -> Image.Image:
        """Applique des transformations aléatoires à l'image"""
        # Rotation légère
        angle = random.uniform(-5, 5)
        img = img.rotate(angle, expand=False, resample=Image.BILINEAR)
        
        # Léger flou
        if random.random() > 0.5:
            img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0, 1)))
        
        return img
    
    def generate_piece_image(self, piece: str, size: Tuple[int, int] = (100, 100)) -> Image.Image:
        """
        Génère une image d'une pièce d'échecs.
        
        Args:
            piece: Symbole de la pièce ('K', 'Q', 'R', etc., ou 'empty')
            size: Taille de l'image en pixels
            
        Returns:
            Image PIL générée
        """
        # Crée le fond
        img = self._create_random_background(size)
        
        if piece != 'empty':
            # Dessine la pièce
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", size[0] // 2)
            except:
                font = ImageFont.load_default()
            
            # Calcule la position pour centrer la pièce
            symbol = self.PIECES[piece]
            bbox = draw.textbbox((0, 0), symbol, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            # Dessine la pièce avec une couleur appropriée
            color = (255, 255, 255) if piece.isupper() else (0, 0, 0)
            draw.text((x, y), symbol, font=font, fill=color)
        
        # Applique les transformations
        img = self._apply_random_transform(img)
        img = self._add_noise(img)
        
        return img
    
    def generate_dataset(self, samples_per_piece: int = 1000):
        """
        Génère un dataset complet.
        
        Args:
            samples_per_piece: Nombre d'échantillons à générer pour chaque type de pièce
        """
        pieces = list(self.PIECES.keys()) + ['empty']
        
        for piece in pieces:
            piece_dir = os.path.join(self.output_dir, piece)
            print(f"Génération des images pour la pièce {piece}...")
            
            for i in range(samples_per_piece):
                img = self.generate_piece_image(piece)
                img.save(os.path.join(piece_dir, f"{piece}_{i:04d}.png"))
                
                if (i + 1) % 100 == 0:
                    print(f"  {i + 1}/{samples_per_piece} images générées")
        
        print("Génération du dataset terminée !")
