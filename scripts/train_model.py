import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import cv2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import logging
from src.piece_classifier import PieceClassifier
from sklearn.model_selection import train_test_split
import tensorflow as tf
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import io
from PIL import Image
import json

# Configure le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_preprocess_data(data_dir: str):
    """Charge et prétraite les images d'entraînement"""
    images = []
    labels = []
    class_mapping = {}
    
    # Parcourt les dossiers de classes
    for i, class_name in enumerate(sorted(os.listdir(data_dir))):
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.isdir(class_dir):
            continue
            
        logger.info(f"Chargement de la classe : {class_name}")
        class_mapping[i] = class_name
        
        # Charge les images de la classe
        for img_name in os.listdir(class_dir):
            img_path = os.path.join(class_dir, img_name)
            try:
                if img_name.lower().endswith('.svg'):
                    # Convertit SVG en PNG en utilisant svglib
                    drawing = svg2rlg(img_path)
                    if drawing:
                        # Convertit en PNG et charge avec PIL
                        img_data = renderPM.drawToString(drawing, fmt='PNG')
                        img = Image.open(io.BytesIO(img_data))
                        img = img.convert('RGB')
                        img = np.array(img)
                    else:
                        logger.warning(f"Impossible de charger le SVG : {img_path}")
                        continue
                else:
                    # Charge l'image normale
                    img = cv2.imread(img_path)
                    if img is None:
                        logger.warning(f"Impossible de charger l'image : {img_path}")
                        continue
                    # Convertit en RGB
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Redimensionne
                img = cv2.resize(img, (100, 100))
                
                # Améliore le contraste
                lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                cl = clahe.apply(l)
                enhanced = cv2.merge((cl,a,b))
                img = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
                
                # Normalise
                img = img.astype(np.float32) / 255.0
                
                images.append(img)
                labels.append(i)
                
            except Exception as e:
                logger.error(f"Erreur lors du chargement de {img_path}: {str(e)}")
                continue
    
    # Convertit en arrays numpy
    images = np.array(images)
    labels = np.array(labels)
    
    # Mélange les données
    indices = np.random.permutation(len(images))
    images = images[indices]
    labels = labels[indices]
    
    return images, labels, class_mapping

def main():
    # Paramètres
    data_dir = "data/pieces"
    model_dir = "models"
    batch_size = 32
    epochs = 100  
    validation_split = 0.2
    
    # Crée le dossier des modèles
    os.makedirs(model_dir, exist_ok=True)
    
    # Charge les données
    logger.info("Chargement des données...")
    X, y, class_mapping = load_and_preprocess_data(data_dir)
    
    # Log class distribution
    unique, counts = np.unique(y, return_counts=True)
    for class_idx, count in zip(unique, counts):
        logger.info(f"Classe {class_mapping[class_idx]}: {count} images")
    
    # Divise en ensembles d'entraînement et de validation
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, 
        test_size=validation_split, 
        random_state=42,
        stratify=y  
    )
    
    # Configuration de l'augmentation des données
    datagen = ImageDataGenerator(
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Calcul du nombre d'images à générer par classe
    unique_classes = np.unique(y_train)
    samples_per_class = {cls: np.sum(y_train == cls) for cls in unique_classes}
    target_samples = 100  # Nombre cible d'échantillons par classe
    
    # Génération des images augmentées
    X_augmented = []
    y_augmented = []
    
    for cls in unique_classes:
        # Sélectionne les images de la classe actuelle
        class_indices = np.where(y_train == cls)[0]
        class_images = X_train[class_indices]
        
        # Calcule combien d'images supplémentaires sont nécessaires
        current_samples = samples_per_class[cls]
        needed_samples = max(0, target_samples - current_samples)
        
        if needed_samples > 0:
            # Ajoute les images originales
            X_augmented.extend(class_images)
            y_augmented.extend([cls] * len(class_images))
            
            # Génère des images augmentées
            augmented_count = 0
            for x_batch in datagen.flow(class_images, batch_size=1):
                X_augmented.append(x_batch[0])
                y_augmented.append(cls)
                augmented_count += 1
                if augmented_count >= needed_samples:
                    break
    
    # Convertit en tableaux numpy
    X_augmented = np.array(X_augmented)
    y_augmented = np.array(y_augmented)
    
    # Combine les données originales et augmentées
    X_train_final = np.concatenate([X_train, X_augmented])
    y_train_final = np.concatenate([y_train, y_augmented])
    
    # Initialise le classifieur et crée le modèle
    classifier = PieceClassifier()
    model = classifier.create_model(num_classes=len(class_mapping))
    
    # Callbacks pour l'entraînement
    callbacks = [
        # Sauvegarde le meilleur modèle
        ModelCheckpoint(
            os.path.join(model_dir, 'best_model.h5'),
            monitor='val_accuracy',
            mode='max',
            save_best_only=True,
            verbose=1
        ),
        # Early stopping pour éviter le surapprentissage
        EarlyStopping(
            monitor='val_accuracy',
            mode='max',
            patience=20,
            restore_best_weights=True,
            verbose=1
        ),
        # Learning rate reduction on plateau
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=10,
            min_lr=1e-6,
            verbose=1
        )
    ]
    
    # Entraîne le modèle
    logger.info("Début de l'entraînement...")
    history = model.fit(
        X_train_final, y_train_final,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )
    
    # Évalue le modèle final
    logger.info("Évaluation du modèle...")
    test_loss, test_acc = model.evaluate(X_val, y_val, verbose=0)
    logger.info(f"Test accuracy: {test_acc:.4f}")
    
    # Sauvegarde le mapping des classes
    with open(os.path.join(model_dir, 'class_mapping.json'), 'w') as f:
        json.dump(class_mapping, f)
    
    logger.info("Entraînement terminé !")

if __name__ == "__main__":
    main()
