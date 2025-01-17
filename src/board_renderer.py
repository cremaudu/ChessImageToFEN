import chess
import chess.svg
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BoardRenderer:
    def __init__(self):
        """Initialise le renderer d'échiquier"""
        self.piece_symbols = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',  # Pièces blanches
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'   # Pièces noires
        }
    
    def render_svg(self, fen: str, size: int = 400) -> str:
        """
        Génère une représentation SVG de l'échiquier.
        
        Args:
            fen: Position en notation FEN
            size: Taille en pixels
            
        Returns:
            Chaîne SVG de l'échiquier
        """
        try:
            board = chess.Board(fen)
            return chess.svg.board(board, size=size)
        except Exception as e:
            logger.error(f"Erreur lors du rendu SVG : {str(e)}")
            return ""
            
    def render_ascii(self, fen: str) -> str:
        """
        Génère une représentation ASCII de l'échiquier.
        
        Args:
            fen: Position en notation FEN
            
        Returns:
            Chaîne ASCII représentant l'échiquier
        """
        try:
            board = chess.Board(fen)
            ascii_board = str(board)
            return ascii_board
        except Exception as e:
            logger.error(f"Erreur lors du rendu ASCII : {str(e)}")
            return ""
