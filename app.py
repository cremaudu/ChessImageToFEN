from flask import Flask, request, jsonify, render_template
import os
from src.image_processor import ImageProcessor
from src.piece_classifier import PieceClassifier
from src.fen_generator import FENGenerator
from src.chess_analyzer import ChessAnalyzer
from src.board_renderer import BoardRenderer
from src.pgn_exporter import PGNExporter
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialisation des composants
image_processor = ImageProcessor()
piece_classifier = PieceClassifier()
fen_generator = FENGenerator()
chess_analyzer = ChessAnalyzer()
board_renderer = BoardRenderer()
pgn_exporter = PGNExporter()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        logger.info("Début du traitement de l'upload")
        if 'file' not in request.files:
            logger.error("Aucun fichier dans la requête")
            return jsonify({'success': False, 'error': 'Aucun fichier reçu'})
        
        file = request.files['file']
        if file.filename == '':
            logger.error("Nom de fichier vide")
            return jsonify({'success': False, 'error': 'Aucun fichier sélectionné'})
        
        # Sauvegarde l'image
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        logger.info(f"Sauvegarde de l'image dans : {filepath}")
        file.save(filepath)
                
        # Traite l'image
        logger.info("Détection de l'échiquier...")
        corners = image_processor.detect_chessboard(filepath)
        if corners is None:
            return jsonify({'success': False, 'error': 'Échiquier non détecté'})
        
        # Extrait les cases
        logger.info("Extraction des cases...")
        squares = image_processor.extract_squares(filepath, corners)
        if not squares or len(squares) != 64:
            return jsonify({'success': False, 'error': 'Erreur lors de l\'extraction des cases'})
        
        # Classifie les pièces
        logger.info("Classification des pièces...")
        pieces = piece_classifier.classify_board(squares)
        
        # Génère le FEN
        logger.info("Génération du FEN...")
        fen = fen_generator.generate_fen(pieces)
        
        # Analyse la position
        logger.info("Analyse de la position...")
        analysis = chess_analyzer.analyze_position(fen)
        analysis_summary = chess_analyzer.get_position_summary(fen)
        
        # Génère le rendu de l'échiquier
        logger.info("Rendu de l'échiquier...")
        board_svg = board_renderer.render_svg(fen)
        
        # Génère le PGN
        logger.info("Génération du PGN...")
        pgn = pgn_exporter.export_pgn(fen, analysis)
        
        # Nettoie le fichier temporaire
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'fen': fen,
            'board_svg': board_svg,
            'analysis_summary': analysis_summary,
            'variations': [
                {
                    'score': result.score,
                    'mate_in': result.mate_in,
                    'best_move': result.best_move,
                    'pv': result.pv
                }
                for result in analysis
            ],
            'pgn': pgn
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement : {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
