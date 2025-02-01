import cv2
import numpy as np
from typing import Tuple, Optional, List
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    VALID_EXTENSIONS = ['.jpg', '.jpeg', '.png']
    MIN_IMAGE_SIZE = 200  # Minimum size in pixels for both width and height
    
    @staticmethod
    def validate_image(image_path: str) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Validate if the image is in a supported format and can be processed.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (is_valid, image_data)
            - is_valid: Boolean indicating if image is valid
            - image_data: np.ndarray of the image if valid, None otherwise
        """
        # Check file extension
        if not any(image_path.lower().endswith(ext) for ext in ImageProcessor.VALID_EXTENSIONS):
            logger.error(f"Invalid image format. Supported formats: {ImageProcessor.VALID_EXTENSIONS}")
            return False, None
            
        try:
            # Read file as binary
            with open(image_path, 'rb') as f:
                img_array = np.frombuffer(f.read(), np.uint8)
            
            # Decode the image
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if image is None:
                logger.error("Failed to load image")
                return False, None
                
            # Check image dimensions
            height, width = image.shape[:2]
            if height < ImageProcessor.MIN_IMAGE_SIZE or width < ImageProcessor.MIN_IMAGE_SIZE:
                logger.error(f"Image too small. Minimum size: {ImageProcessor.MIN_IMAGE_SIZE}x{ImageProcessor.MIN_IMAGE_SIZE}")
                return False, None
                
            return True, image
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return False, None
            
    def detect_chessboard(self, image_path: str) -> Tuple[bool, Optional[np.ndarray]]:
        """Détecte l'échiquier dans l'image et retourne ses coins"""
        try:
            # Charge l'image
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Impossible de charger l'image : {image_path}")
                return False, None

            # Convertit en niveaux de gris
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Applique un flou gaussien pour réduire le bruit
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Détecte les coins de l'échiquier
            ret, corners = cv2.findChessboardCorners(blurred, (7, 7), None)
            
            if ret:
                # Affine la position des coins
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                
                # Log des informations sur les coins
                logger.info(f"Nombre de coins détectés : {len(corners)}")
                logger.info(f"Forme des coins : {corners.shape}")
                
                # Sauvegarde l'image avec les coins détectés pour le debug
                debug_img = img.copy()
                cv2.drawChessboardCorners(debug_img, (7, 7), corners, ret)
                debug_dir = 'debug'
                os.makedirs(debug_dir, exist_ok=True)
                debug_path = os.path.join(debug_dir, 'detected_corners.png')
                cv2.imwrite(debug_path, debug_img)
                logger.info(f"Image avec coins détectés sauvegardée : {debug_path}")
                
                # Extrapoler les coins externes
                # Calcule la taille moyenne d'une case
                square_size = np.mean([
                    np.linalg.norm(corners[1] - corners[0]),
                    np.linalg.norm(corners[7] - corners[0])
                ])
                logger.info(f"Taille moyenne d'une case : {square_size:.2f} pixels")
                
                # Calcule les coins externes
                corners = corners.reshape(-1, 2)
                top_left = corners[0] - square_size
                top_right = corners[6] + np.array([square_size, -square_size])
                bottom_right = corners[-1] + square_size
                bottom_left = corners[-7] + np.array([-square_size, square_size])
                
                # Crée un tableau avec les 4 coins externes
                board_corners = np.array([
                    top_left, top_right, bottom_right, bottom_left
                ], dtype=np.float32)
                
                # Dessine les coins externes sur l'image de debug
                debug_img = img.copy()
                for i, corner in enumerate(board_corners):
                    cv2.circle(debug_img, tuple(corner.astype(int)), 5, (0, 0, 255), -1)
                    if i > 0:
                        cv2.line(debug_img, 
                                tuple(board_corners[i-1].astype(int)),
                                tuple(corner.astype(int)),
                                (0, 255, 0), 2)
                cv2.line(debug_img,
                        tuple(board_corners[-1].astype(int)),
                        tuple(board_corners[0].astype(int)),
                        (0, 255, 0), 2)
                debug_path = os.path.join(debug_dir, 'board_corners.png')
                cv2.imwrite(debug_path, debug_img)
                logger.info(f"Image avec coins de l'échiquier sauvegardée : {debug_path}")
                
                logger.info("Coins de l'échiquier extrapolés avec succès")
                logger.info(f"Coins : {board_corners}")
                
                return True, board_corners
            else:
                logger.error("Pas de coins d'échiquier détectés")
                return False, None
            
        except Exception as e:
            logger.error(f"Error detecting chessboard: {str(e)}")
            return False, None

    def extract_squares(self, image_path: str, corners: np.ndarray) -> Tuple[bool, List[np.ndarray]]:
        """Extrait les 64 cases de l'échiquier"""
        try:
            # Charge l'image
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Impossible de charger l'image : {image_path}")
                return False, []

            # Convertit en RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Trie les coins pour avoir un ordre cohérent
            corners = self._sort_corners(corners)
            
            # Calcule la matrice de perspective
            width = height = 800  # Taille plus grande pour une meilleure qualité
            dst_points = np.array([
                [0, 0],
                [width - 1, 0],
                [width - 1, height - 1],
                [0, height - 1]
            ], dtype=np.float32)
            
            # Applique la transformation de perspective
            matrix = cv2.getPerspectiveTransform(corners, dst_points)
            warped = cv2.warpPerspective(img, matrix, (width, height))
            
            # Extrait chaque case
            square_size = width // 8
            squares = []
            
            for row in range(8):
                for col in range(8):
                    x = col * square_size
                    y = row * square_size
                    square = warped[y:y + square_size, x:x + square_size]
                    
                    # Ajoute une marge autour de la case pour éviter les effets de bord
                    margin = square_size // 10
                    square = cv2.copyMakeBorder(
                        square,
                        margin, margin, margin, margin,
                        cv2.BORDER_CONSTANT,
                        value=[255, 255, 255]
                    )
                    
                    # Redimensionne à la taille attendue par le modèle
                    square = cv2.resize(square, (100, 100))
                    squares.append(square)
            
            return True, squares
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des cases : {str(e)}")
            return False, []

    def _sort_corners(self, corners: np.ndarray) -> np.ndarray:
        """Trie les coins dans l'ordre : haut-gauche, haut-droite, bas-droite, bas-gauche"""
        # Calcule le centre des coins
        center = np.mean(corners, axis=0)
        
        # Pour chaque coin, calcule l'angle par rapport au centre
        angles = np.arctan2(corners[:, 1] - center[1],
                          corners[:, 0] - center[0])
        
        # Trie les coins par angle
        sorted_indices = np.argsort(angles)
        sorted_corners = corners[sorted_indices]
        
        # Trouve le coin le plus en haut à gauche (plus petite somme x+y)
        distances = np.sum(sorted_corners, axis=1)
        start_idx = np.argmin(distances)
        
        # Réorganise les coins pour commencer par le coin haut-gauche
        sorted_corners = np.roll(sorted_corners, -start_idx, axis=0)
        
        return sorted_corners.astype(np.float32)
