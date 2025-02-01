import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import logging
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from src.piece_classifier import PieceClassifier

# Configure le logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_test_data(test_dir: str):
    """Charge les données de test"""
    images = []
    labels = []
    true_classes = []
    
    # Parcourt les dossiers de classes
    for class_name in sorted(os.listdir(test_dir)):
        class_dir = os.path.join(test_dir, class_name)
        if not os.path.isdir(class_dir):
            continue
            
        logger.info(f"Chargement des images de test pour : {class_name}")
        
        # Charge les images de la classe
        for img_name in os.listdir(class_dir):
            img_path = os.path.join(class_dir, img_name)
            try:
                # Charge et prétraite l'image
                img = cv2.imread(img_path)
                if img is None:
                    continue
                
                # Prétraite l'image comme dans l'entraînement
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (100, 100))
                
                # Améliore le contraste
                lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                cl = clahe.apply(l)
                enhanced = cv2.merge((cl,a,b))
                img = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
                
                img = img.astype(np.float32) / 255.0
                
                images.append(img)
                true_classes.append(class_name)
                
            except Exception as e:
                logger.error(f"Erreur lors du chargement de {img_path}: {str(e)}")
                continue
                
    return np.array(images), true_classes

def plot_confusion_matrix(y_true, y_pred, classes):
    """Affiche la matrice de confusion"""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes)
    plt.title('Matrice de confusion')
    plt.ylabel('Vraie classe')
    plt.xlabel('Classe prédite')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    plt.close()

def main():
    # Paramètres
    test_dir = "data/test_pieces"
    model_path = "models/best_model.h5"
    
    # Charge le modèle
    logger.info("Chargement du modèle...")
    classifier = PieceClassifier()
    model = classifier.load_model(model_path)
    
    # Charge les données de test
    logger.info("Chargement des données de test...")
    X_test, true_classes = load_test_data(test_dir)
    
    # Fait les prédictions
    logger.info("Prédiction sur les données de test...")
    predictions = model.predict(X_test)
    predicted_classes = [classifier.PIECES[np.argmax(pred)] for pred in predictions]
    
    # Affiche le rapport de classification
    logger.info("\nRapport de classification :")
    print(classification_report(true_classes, predicted_classes))
    
    # Affiche la matrice de confusion
    plot_confusion_matrix(true_classes, predicted_classes, sorted(set(true_classes)))
    logger.info("Matrice de confusion sauvegardée dans confusion_matrix.png")

if __name__ == "__main__":
    main()
