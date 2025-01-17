import pytest
import numpy as np
from src.piece_classifier import PieceClassifier

@pytest.fixture
def classifier():
    return PieceClassifier()

def test_preprocess_square(classifier):
    # Test avec une image de la bonne taille
    square = np.zeros((100, 100, 3), dtype=np.uint8)
    processed = classifier.preprocess_square(square)
    assert processed.shape == (1, 100, 100, 3)
    assert processed.dtype == np.float32
    assert np.max(processed) <= 1.0
    
    # Test avec une image de taille différente
    square = np.zeros((200, 200, 3), dtype=np.uint8)
    processed = classifier.preprocess_square(square)
    assert processed.shape == (1, 100, 100, 3)

@pytest.mark.skip(reason="Le modèle n'est pas encore entraîné")
def test_classify_square(classifier):
    # Test avec une case vide
    square = np.zeros((100, 100, 3), dtype=np.uint8)
    piece = classifier.classify_square(square)
    assert piece in PieceClassifier.PIECES.values()
    
    # Test avec une case invalide
    square = np.zeros((10, 10), dtype=np.uint8)  # Mauvaise forme
    piece = classifier.classify_square(square)
    assert piece == 'empty'  # Devrait retourner empty en cas d'erreur

@pytest.mark.skip(reason="Le modèle n'est pas encore entraîné")
def test_classify_board(classifier):
    # Crée un échiquier de test
    squares = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(64)]
    pieces = classifier.classify_board(squares)
    
    assert len(pieces) == 64
    assert all(p in PieceClassifier.PIECES.values() for p in pieces)
