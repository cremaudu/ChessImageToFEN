import chess
import chess.pgn
from datetime import datetime
import io
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PGNExporter:
    def __init__(self):
        """Initialise l'exporteur PGN"""
        pass
    
    def create_game(self, fen: str, headers: Optional[Dict[str, str]] = None) -> chess.pgn.Game:
        """
        Crée un objet Game à partir d'une position FEN.
        
        Args:
            fen: Position en notation FEN
            headers: En-têtes PGN optionnels
            
        Returns:
            Objet Game représentant la partie
        """
        try:
            # Crée une nouvelle partie
            game = chess.pgn.Game()
            
            # Définit la position initiale
            board = chess.Board(fen)
            game.setup(board)
            
            # Ajoute les en-têtes par défaut
            game.headers["Event"] = "Chess Position Analysis"
            game.headers["Site"] = "ChessImageToFEN"
            game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
            game.headers["Round"] = "1"
            game.headers["White"] = "?"
            game.headers["Black"] = "?"
            game.headers["Result"] = "*"
            game.headers["FEN"] = fen
            game.headers["SetUp"] = "1"
            
            # Ajoute les en-têtes personnalisés
            if headers:
                for key, value in headers.items():
                    game.headers[key] = value
            
            return game
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la partie : {str(e)}")
            return None
    
    def export_pgn(self, fen: str, analysis_results: Optional[list] = None, headers: Optional[Dict[str, str]] = None) -> str:
        """
        Exporte une position en format PGN avec analyse optionnelle.
        
        Args:
            fen: Position en notation FEN
            analysis_results: Résultats d'analyse optionnels (de ChessAnalyzer)
            headers: En-têtes PGN optionnels
            
        Returns:
            Chaîne PGN
        """
        try:
            # Crée la partie
            game = self.create_game(fen, headers)
            if game is None:
                return ""
            
            # Ajoute les commentaires d'analyse
            if analysis_results:
                node = game.add_line([])
                
                # Ajoute chaque variante
                for i, result in enumerate(analysis_results):
                    if i == 0:
                        # Première ligne = évaluation principale
                        comment = f"Évaluation: "
                        if result.mate_in is not None:
                            comment += f"Mat en {result.mate_in}"
                        else:
                            comment += f"{result.score/100:.2f}"
                        node.comment = comment
                        
                        # Ajoute la ligne principale
                        if result.pv:
                            node.add_line([chess.Move.from_uci(m) for m in result.pv])
                    else:
                        # Autres lignes = variantes
                        if result.pv:
                            var_node = node.add_variation(chess.Move.from_uci(result.pv[0]))
                            comment = f"Variante {i+1}"
                            if result.mate_in is not None:
                                comment += f" (Mat en {result.mate_in})"
                            else:
                                comment += f" ({result.score/100:.2f})"
                            var_node.comment = comment
                            
                            # Ajoute le reste de la variante
                            for move in result.pv[1:]:
                                var_node = var_node.add_variation(chess.Move.from_uci(move))
            
            # Exporte en PGN
            exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
            pgn_string = game.accept(exporter)
            
            return pgn_string
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export PGN : {str(e)}")
            return ""
    
    def save_pgn(self, pgn: str, output_path: str) -> bool:
        """
        Sauvegarde une chaîne PGN dans un fichier.
        
        Args:
            pgn: Chaîne PGN
            output_path: Chemin de sortie pour le fichier PGN
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(pgn)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde PGN : {str(e)}")
            return False
