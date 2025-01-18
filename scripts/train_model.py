import tensorflow as tf
import numpy as np
import cv2
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_images(data_dir: str):
    """Charge les images d'entraînement et leurs étiquettes"""
    images = []
    labels = []
    piece_to_label = {
        'empty': 0,
        'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,  # Pièces blanches
        'p': 7, 'n': 8, 'b': 9, 'r': 10, 'q': 11, 'k': 12  # Pièces noires
    }
    
    # Parcourt chaque dossier de pièces
    for piece_type in piece_to_label.keys():
        piece_dir = os.path.join(data_dir, piece_type)
        if not os.path.exists(piece_dir):
            continue
            
        # Charge chaque image du dossier
        for img_file in os.listdir(piece_dir):
            if not img_file.endswith(('.png', '.jpg', '.jpeg')):
                continue
                
            img_path = os.path.join(piece_dir, img_file)
            try:
                # Lit et prétraite l'image
                img = cv2.imread(img_path)
                if img is None:
                    logger.warning(f"Impossible de lire l'image : {img_path}")
                    continue
                    
                # Convertit en RGB et redimensionne
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (100, 100))
                img = img.astype(np.float32) / 255.0
                
                # Pour les pièces blanches, crée aussi une version noire
                if piece_type.isupper():  # Si c'est une pièce blanche
                    # Version blanche
                    images.append(img)
                    labels.append(piece_to_label[piece_type])
                    
                    # Version noire (convertie)
                    black_piece_type = piece_type.lower()
                    images.append(img)  # Même image pour l'instant
                    labels.append(piece_to_label[black_piece_type])
                else:
                    # Cases vides
                    images.append(img)
                    labels.append(piece_to_label[piece_type])
                    
            except Exception as e:
                logger.error(f"Erreur lors du chargement de {img_path}: {str(e)}")
                continue
    
    return np.array(images), np.array(labels)

def create_model():
    """Crée le modèle CNN"""
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(100, 100, 3)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(13, activation='softmax')  # 13 classes (vide + 6 pièces x 2 couleurs)
    ])
    
    model.compile(optimizer='adam',
                 loss='sparse_categorical_crossentropy',
                 metrics=['accuracy'])
    return model

def train_model():
    """Entraîne le modèle sur les nouvelles images"""
    # Charge les images
    logger.info("Chargement des images...")
    images, labels = load_images('data/pieces')
    
    # Crée et entraîne le modèle
    logger.info("Création du modèle...")
    model = create_model()
    
    # Crée le dossier models s'il n'existe pas
    os.makedirs('models', exist_ok=True)
    
    # Définit un callback pour sauvegarder le meilleur modèle
    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        'models/chess_piece_classifier.h5',
        save_best_only=True,
        monitor='val_accuracy',
        mode='max'
    )
    
    # Entraîne le modèle
    logger.info("Début de l'entraînement...")
    model.fit(
        images, labels,
        epochs=50,
        validation_split=0.2,
        callbacks=[checkpoint],
        verbose=1
    )
    
    logger.info("Entraînement terminé!")

if __name__ == "__main__":
    train_model()
