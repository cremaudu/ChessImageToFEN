# ImageToFEN

Application web permettant d'analyser une image d'échiquier et de la convertir en notation FEN (Forsyth–Edwards Notation).

## Installation

1. Créer un environnement virtuel Python :
```bash
python -m venv venv
```

2. Activer l'environnement virtuel :
```bash
# Windows
venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Lancement de l'application

```bash
python app.py
```

L'application sera accessible à l'adresse : http://localhost:5000

## Structure du projet

```
ImageToFEN/
├── static/          # Fichiers statiques (CSS, JS, images)
├── templates/       # Templates HTML
├── app.py          # Application Flask principale
├── chess_vision/   # Module de détection d'échiquier
└── requirements.txt # Dépendances Python
```
