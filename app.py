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
        logger.info("=== Début du traitement de l'upload ===")
        if 'file' not in request.files:
            logger.error("Aucun fichier dans la requête")
            return jsonify({'success': False, 'error': 'Aucun fichier reçu'})
        
        file = request.files['file']
        logger.info(f"Fichier reçu: {file.filename}")
        
        if file.filename == '':
            logger.error("Nom de fichier vide")
            return jsonify({'success': False, 'error': 'Aucun fichier sélectionné'})
        
        # Sauvegarde l'image
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        logger.info(f"Tentative de sauvegarde de l'image dans : {filepath}")
        file.save(filepath)
        logger.info("Image sauvegardée avec succès")
                
        # Traite l'image
        logger.info("Début de la détection de l'échiquier...")
        success, corners = image_processor.detect_chessboard(filepath)
        logger.info(f"Résultat de la détection des coins: {success}")
        
        if not success or corners is None:
            logger.error("Échec de la détection de l'échiquier - coins non trouvés")
            return jsonify({'success': False, 'error': 'Échiquier non détecté'})
        
        # Extrait les cases
        logger.info("Début de l'extraction des cases...")
        success, squares = image_processor.extract_squares(filepath, corners)
        logger.info(f"Nombre de cases extraites: {len(squares) if squares else 0}")
        
        if not success or not squares or len(squares) != 64:
            logger.error(f"Échec de l'extraction des cases - nombre incorrect de cases: {len(squares) if squares else 0}")
            return jsonify({'success': False, 'error': 'Erreur lors de l\'extraction des cases'})
        
        # Classifie les pièces
        logger.info("Classification des pièces...")
        pieces = piece_classifier.classify_board(squares)
        
        # Génère le FEN
        logger.info("Génération du FEN...")
        try:
            fen = fen_generator.pieces_to_fen(pieces)
            logger.info(f"FEN généré : {fen}")
        except Exception as e:
            logger.error(f"Erreur lors de la génération du FEN : {str(e)}")
            return jsonify({'success': False, 'error': 'Erreur lors de la génération du FEN'})
        
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
    # S'assurer que le dossier d'upload existe
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Configuration du serveur
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB pour les uploads
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Démarrer le serveur
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
