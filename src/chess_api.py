from flask import Blueprint, request, jsonify
from .chess_detector import ChessboardDetector

api = Blueprint('api', __name__)
detector = ChessboardDetector()

@api.route('/analyze', methods=['POST'])
def analyze_image():
    """Endpoint pour analyser une image d'échiquier et retourner la notation FEN"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    image_file = request.files['image']
    
    # Validation du format
    if not detector.validate_image_format(image_file):
        return jsonify({'error': 'Invalid image format. Only JPG and PNG are supported'}), 400
    
    # TODO: Implémenter l'analyse d'image et la conversion en FEN
    return jsonify({'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'})
