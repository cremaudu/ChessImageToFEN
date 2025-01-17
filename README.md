# Chess Image to FEN

Une application web qui analyse une image d'échiquier et génère la notation FEN correspondante.

## Fonctionnalités

- **Détection d'échiquier** : Détecte automatiquement l'échiquier dans l'image
- **Extraction de la grille** : Extrait les 64 cases avec correction de perspective
- **Reconnaissance des pièces** : Identifie les pièces sur chaque case avec un modèle CNN
- **Génération FEN** : Convertit la position en notation FEN standard
- **Interface web** : Interface utilisateur simple et intuitive

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/yourusername/ChessImageToFEN.git
cd ChessImageToFEN
```

2. Créez un environnement virtuel Python et activez-le :
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Démarrez le serveur Flask :
```bash
python app.py
```

2. Ouvrez votre navigateur à l'adresse http://localhost:5000

3. Téléchargez une image d'échiquier ou prenez une photo

4. Cliquez sur "Analyser" pour obtenir la notation FEN

## Structure du projet

```
ChessImageToFEN/
├── src/
│   ├── image_processor.py    # Traitement d'image et détection
│   ├── piece_classifier.py   # Classification des pièces
│   └── fen_generator.py      # Génération de la notation FEN
├── tests/
│   └── test_*.py            # Tests unitaires
├── data/
│   └── pieces/              # Images d'entraînement
├── models/
│   └── chess_piece_classifier.h5  # Modèle entraîné
├── static/
│   └── uploads/             # Images téléchargées
├── templates/
│   └── index.html           # Interface utilisateur
├── app.py                   # Application Flask
├── train_model.py          # Script d'entraînement
└── requirements.txt        # Dépendances Python
```

## Entraînement du modèle

Pour entraîner le modèle de reconnaissance des pièces :

1. Générez le dataset d'entraînement :
```bash
python train_model.py
```

2. Le modèle entraîné sera sauvegardé dans `models/chess_piece_classifier.h5`

## Tests

Pour lancer les tests :
```bash
python -m pytest
```

## Limitations actuelles

- Nécessite une image de bonne qualité avec un bon éclairage
- L'échiquier doit être visible en entier dans l'image
- Les pièces doivent être de style standard

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
