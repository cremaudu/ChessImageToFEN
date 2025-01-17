from src.dataset_generator import DatasetGenerator
from src.model_trainer import ChessModelTrainer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Génération du dataset
    logger.info("Génération du dataset...")
    generator = DatasetGenerator()
    generator.generate_dataset(samples_per_piece=1000)  # 1000 images par type de pièce
    
    # Entraînement du modèle
    logger.info("Entraînement du modèle...")
    trainer = ChessModelTrainer()
    history = trainer.train(epochs=20)
    
    # Affiche les résultats
    final_accuracy = history.history['accuracy'][-1]
    final_val_accuracy = history.history['val_accuracy'][-1]
    logger.info(f"Entraînement terminé !")
    logger.info(f"Précision finale : {final_accuracy:.2%}")
    logger.info(f"Précision de validation : {final_val_accuracy:.2%}")

if __name__ == '__main__':
    main()
