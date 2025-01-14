import pytest
import sys
import os

# Ajouter le répertoire src au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def sample_image():
    """Fixture pour fournir une image test"""
    # Sera implémenté plus tard avec une image de test
    pass
