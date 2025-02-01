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
        0: 'B',  # Bishop (Fou)
        1: 'empty',  # Case vide
        2: 'K',  # King (Roi)
        3: 'N',  # Knight (Cavalier)
        4: 'P',  # Pawn (Pion)
        5: 'Q',  # Queen (Dame)
        6: 'R'   # Rook (Tour)
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
    
    def create_model(self, num_classes):
        """Crée un nouveau modèle CNN avec une architecture améliorée"""
        model = tf.keras.Sequential([
            # Premier bloc convolutif
            tf.keras.layers.Conv2D(64, (3, 3), padding='same', input_shape=(100, 100, 3)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Activation('relu'),
            tf.keras.layers.Conv2D(64, (3, 3), padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Activation('relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.3),
            
            # Deuxième bloc convolutif
            tf.keras.layers.Conv2D(128, (3, 3), padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Activation('relu'),
            tf.keras.layers.Conv2D(128, (3, 3), padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Activation('relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.3),
            
            # Troisième bloc convolutif
            tf.keras.layers.Conv2D(256, (3, 3), padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Activation('relu'),
            tf.keras.layers.Conv2D(256, (3, 3), padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Activation('relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.3),
            
            # Couches denses
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(512),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Activation('relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile le modèle avec un optimiseur amélioré
        optimizer = tf.keras.optimizers.Adam(
            learning_rate=0.001,
            beta_1=0.9,
            beta_2=0.999,
            epsilon=1e-07
        )
        
        model.compile(
            optimizer=optimizer,
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.SparseTopKCategoricalAccuracy(k=2, name='top_2_accuracy')]
        )
        
        return model
        
    def preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Prétraite une image pour la classification"""
        try:
            # Convert RGBA to RGB if necessary
            if img.shape[-1] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            elif len(img.shape) == 2:  # Grayscale
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                
            # Resize
            img = cv2.resize(img, (100, 100))
            
            # Enhance contrast using CLAHE
            lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            enhanced = cv2.merge((cl,a,b))
            img = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
            
            # Add additional preprocessing steps
            # 1. Gaussian blur to reduce noise
            img = cv2.GaussianBlur(img, (3, 3), 0)
            
            # 2. Normalize pixel values
            img = img.astype(np.float32) / 255.0
            
            # 3. Standardize
            mean = np.mean(img)
            std = np.std(img)
            img = (img - mean) / (std + 1e-7)
            
            return img
            
        except Exception as e:
            logger.error(f"Erreur lors du prétraitement de l'image : {str(e)}")
            raise

    def classify_square(self, image: np.ndarray, debug_prefix: Optional[str] = None) -> Tuple[str, float]:
        """Classifie une case de l'échiquier"""
        try:
            # Sauvegarde l'image originale pour le debug
            if debug_prefix:
                debug_dir = os.path.join('debug', 'squares')
                os.makedirs(debug_dir, exist_ok=True)
                cv2.imwrite(os.path.join(debug_dir, f'{debug_prefix}_original.png'), image)
            
            # Prétraite l'image
            processed = self.preprocess_image(image)
            if processed is None:
                return 'empty', 0.0
                
            # Sauvegarde l'image prétraitée pour le debug
            if debug_prefix:
                processed_debug = (processed * 255).astype(np.uint8)
                cv2.imwrite(os.path.join(debug_dir, f'{debug_prefix}_processed.png'), 
                           cv2.cvtColor(processed_debug, cv2.COLOR_RGB2BGR))
            
            # Prépare l'image pour le modèle
            processed = np.expand_dims(processed, axis=0)
            
            # Fait la prédiction
            predictions = self.model.predict(processed, verbose=0)[0]
            
            # Log les probabilités pour chaque classe
            logger.info("Prédictions pour la case :")
            for class_name, prob in zip(self.PIECES.values(), predictions):
                logger.info(f"  {class_name}: {prob*100:.2f}%")
            
            # Trouve la classe avec la plus haute probabilité
            max_prob = np.max(predictions)
            if max_prob < 0.3:  # Augmente le seuil de confiance à 30%
                predicted_class = 'empty'
            else:
                predicted_class = list(self.PIECES.values())[np.argmax(predictions)]
            
            logger.info(f"Classe choisie : {predicted_class} (confiance : {max_prob*100:.2f}%)")
            
            return predicted_class, max_prob
            
        except Exception as e:
            logger.error(f"Erreur lors de la classification : {str(e)}")
            return 'empty', 0.0
    
    def classify_board(self, squares: List[np.ndarray]) -> List[str]:
        """Classifie toutes les cases d'un échiquier"""
        try:
            if len(squares) != 64:
                raise ValueError(f"Expected 64 squares, got {len(squares)}")
            
            pieces = []
            for i, square in enumerate(squares):
                piece, _ = self.classify_square(square)
                pieces.append(piece)
                if (i + 1) % 8 == 0:
                    logger.debug(f"Rang {i//8 + 1} : {' '.join(pieces[-8:])}")
            
            return pieces
            
        except Exception as e:
            logger.error(f"Erreur lors de la classification de l'échiquier : {str(e)}")
            return ['empty'] * 64  # Par défaut, retourne un échiquier vide
