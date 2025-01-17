import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from PIL import Image
from typing import Tuple, List
import random

class ChessModelTrainer:
    def __init__(self, data_dir: str = 'data/pieces'):
        """
        Initialise l'entraîneur du modèle.
        
        Args:
            data_dir: Répertoire contenant les images d'entraînement
        """
        self.data_dir = data_dir
        self.piece_mapping = {
            'empty': 0,
            'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,  # Pièces blanches
            'p': 7, 'n': 8, 'b': 9, 'r': 10, 'q': 11, 'k': 12  # Pièces noires
        }
        self.inv_piece_mapping = {v: k for k, v in self.piece_mapping.items()}
    
    def _load_image(self, image_path: str) -> np.ndarray:
        """Charge et prétraite une image"""
        img = Image.open(image_path)
        img = img.resize((100, 100))
        img_array = np.array(img) / 255.0
        return img_array
    
    def prepare_dataset(self, validation_split: float = 0.2) -> Tuple[tf.data.Dataset, tf.data.Dataset]:
        """
        Prépare les datasets d'entraînement et de validation.
        
        Args:
            validation_split: Proportion des données à utiliser pour la validation
            
        Returns:
            Dataset d'entraînement et dataset de validation
        """
        images = []
        labels = []
        
        # Charge toutes les images
        for piece in self.piece_mapping.keys():
            piece_dir = os.path.join(self.data_dir, piece)
            if not os.path.exists(piece_dir):
                continue
                
            for img_file in os.listdir(piece_dir):
                if not img_file.endswith(('.png', '.jpg', '.jpeg')):
                    continue
                    
                img_path = os.path.join(piece_dir, img_file)
                try:
                    img_array = self._load_image(img_path)
                    images.append(img_array)
                    labels.append(self.piece_mapping[piece])
                except Exception as e:
                    print(f"Erreur lors du chargement de {img_path}: {str(e)}")
        
        # Convertit en arrays numpy
        images = np.array(images)
        labels = np.array(labels)
        
        # Mélange les données
        indices = np.arange(len(images))
        np.random.shuffle(indices)
        images = images[indices]
        labels = labels[indices]
        
        # Divise en ensembles d'entraînement et de validation
        split_idx = int(len(images) * (1 - validation_split))
        train_images = images[:split_idx]
        train_labels = labels[:split_idx]
        val_images = images[split_idx:]
        val_labels = labels[split_idx:]
        
        # Crée les datasets TensorFlow
        train_ds = tf.data.Dataset.from_tensor_slices((train_images, train_labels))
        val_ds = tf.data.Dataset.from_tensor_slices((val_images, val_labels))
        
        # Configure les datasets pour les performances
        BATCH_SIZE = 32
        train_ds = train_ds.shuffle(10000).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
        val_ds = val_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
        
        return train_ds, val_ds
    
    def create_model(self) -> tf.keras.Model:
        """Crée le modèle CNN"""
        model = models.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(100, 100, 3)),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.Flatten(),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(len(self.piece_mapping), activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, epochs: int = 10, model_path: str = 'models/chess_piece_classifier.h5'):
        """
        Entraîne le modèle.
        
        Args:
            epochs: Nombre d'époques d'entraînement
            model_path: Chemin où sauvegarder le modèle
        """
        # Crée le dossier models s'il n'existe pas
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Prépare les données
        train_ds, val_ds = self.prepare_dataset()
        
        # Crée et entraîne le modèle
        model = self.create_model()
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.ModelCheckpoint(
                model_path,
                save_best_only=True,
                monitor='val_accuracy'
            ),
            tf.keras.callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=3,
                restore_best_weights=True
            )
        ]
        
        # Entraînement
        history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=epochs,
            callbacks=callbacks
        )
        
        return history
