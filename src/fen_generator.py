from typing import List
import chess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FENGenerator:
    @staticmethod
    def pieces_to_fen(pieces: List[str]) -> str:
        """
        Convertit une liste de 64 symboles de pièces en notation FEN.
        
        Args:
            pieces: Liste de 64 symboles de pièces (a1, b1, ..., h8)
            
        Returns:
            Chaîne FEN représentant la position
        """
        try:
            # Vérifie que nous avons exactement 64 pièces
            if len(pieces) != 64:
                raise ValueError(f"Expected 64 pieces, got {len(pieces)}")
            
            # Convertit la liste en tableau 8x8
            board = [pieces[i:i+8] for i in range(0, 64, 8)]
            
            # Génère la partie position de la notation FEN
            fen_parts = []
            for rank in board:
                empty_count = 0
                rank_str = ""
                
                for piece in rank:
                    if piece == 'empty':
                        empty_count += 1
                    else:
                        if empty_count > 0:
                            rank_str += str(empty_count)
                            empty_count = 0
                        rank_str += piece
                
                if empty_count > 0:
                    rank_str += str(empty_count)
                
                fen_parts.append(rank_str)
            
            position = '/'.join(fen_parts)
            
            # Par défaut, on suppose que c'est aux blancs de jouer,
            # pas de roque possible, pas de prise en passant
            return f"{position} w - - 0 1"
            
        except Exception as e:
            logger.error(f"Error generating FEN: {str(e)}")
            return "8/8/8/8/8/8/8/8 w - - 0 1"  # Échiquier vide par défaut
    
    @staticmethod
    def validate_fen(fen: str) -> bool:
        """Vérifie si une chaîne FEN est valide"""
        try:
            chess.Board(fen)
            return True
        except ValueError:
            return False
