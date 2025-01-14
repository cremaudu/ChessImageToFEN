import cv2
import numpy as np
from PIL import Image

class ChessboardDetector:
    """Classe pour la détection et l'analyse d'un échiquier dans une image"""
    
    def __init__(self):
        pass
    
    def validate_image_format(self, image_path):
        """Valide le format de l'image
        
        Args:
            image_path (str): Chemin vers l'image à valider
            
        Returns:
            bool: True si le format est valide, False sinon
        """
        try:
            with Image.open(image_path) as img:
                return img.format.lower() in ['jpeg', 'jpg', 'png']
        except Exception:
            return False
