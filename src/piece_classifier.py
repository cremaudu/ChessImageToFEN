import cv2
import numpy as np
import tensorflow as tf
from typing import List, Tuple, Optional
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PieceClassifier:
    # Mapping des indices aux pièces
    PIECES = {
        0: 'empty',
        1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K',  # Pièces blanches
        7: 'p', 8: 'n', 9: 'b', 10: 'r', 11: 'q', 12: 'k'  # Pièces noires
    }
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialise le classifieur de pièces.
        Si model_path est None, cherche le modèle dans le dossier models.
        """
        if model_path is None:
            model_path = os.path.join('models', 'chess_piece_classifier.h5')
        
        if os.path.exists(model_path):
            try:
                self.model = tf.keras.models.load_model(model_path)
                logger.info(f"Modèle chargé depuis {model_path}")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du modèle : {str(e)}")
                self.model = self._create_default_model()
        else:
            logger.warning(f"Modèle non trouvé à {model_path}, création d'un modèle par défaut")
            self.model = self._create_default_model()
            
    def _create_default_model(self) -> tf.keras.Model:
        """Crée un modèle CNN simple pour la classification des pièces"""
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(100, 100, 3)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(len(self.PIECES), activation='softmax')
        ])
        model.compile(optimizer='adam',
                     loss='sparse_categorical_crossentropy',
                     metrics=['accuracy'])
        return model
    
    def preprocess_square(self, square: np.ndarray) -> np.ndarray:
        """Prétraite une image de case d'échiquier pour la classification"""
        try:
            # Redimensionne à 100x100 si nécessaire
            if square.shape[:2] != (100, 100):
                square = cv2.resize(square, (100, 100))
            
            # S'assure que l'image est en RGB
            if len(square.shape) == 2:  # Image en niveaux de gris
                square = cv2.cvtColor(square, cv2.COLOR_GRAY2RGB)
            elif square.shape[2] == 4:  # Image RGBA
                square = cv2.cvtColor(square, cv2.COLOR_RGBA2RGB)
            
            # Normalise les valeurs des pixels
            square = square.astype(np.float32) / 255.0
            
            # Ajoute une dimension de batch
            return np.expand_dims(square, axis=0)
            
        except Exception as e:
            logger.error(f"Erreur lors du prétraitement : {str(e)}")
            # Retourne une image noire en cas d'erreur
            return np.zeros((1, 100, 100, 3), dtype=np.float32)
    
    def classify_square(self, square: np.ndarray) -> str:
        """Classifie une case d'échiquier et retourne le symbole de la pièce"""
        try:
            # Prétraite l'image
            processed = self.preprocess_square(square)
            
            # Fait la prédiction
            prediction = self.model.predict(processed, verbose=0)
            class_idx = np.argmax(prediction[0])
            
            # Calcule la confiance
            confidence = prediction[0][class_idx]
            
            # Si la confiance est trop faible, considère la case comme vide
            if confidence < 0.5:
                logger.debug(f"Confiance faible ({confidence:.2%}), case considérée comme vide")
                return 'empty'
            
            # Retourne le symbole de la pièce
            piece = self.PIECES[class_idx]
            logger.debug(f"Pièce détectée : {piece} (confiance : {confidence:.2%})")
            return piece
            
        except Exception as e:
            logger.error(f"Erreur lors de la classification : {str(e)}")
            return 'empty'  # Par défaut, considère la case comme vide
    
    def classify_board(self, squares: List[np.ndarray]) -> List[str]:
        """Classifie toutes les cases d'un échiquier"""
        try:
            if len(squares) != 64:
                raise ValueError(f"Expected 64 squares, got {len(squares)}")
            
            pieces = []
            for i, square in enumerate(squares):
                piece = self.classify_square(square)
                pieces.append(piece)
                if (i + 1) % 8 == 0:
                    logger.debug(f"Rang {i//8 + 1} : {' '.join(pieces[-8:])}")
            
            return pieces
            
        except Exception as e:
            logger.error(f"Erreur lors de la classification de l'échiquier : {str(e)}")
            return ['empty'] * 64  # Par défaut, retourne un échiquier vide
