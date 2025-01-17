import chess
import chess.engine
import os
import platform
import logging
from typing import Optional, Tuple, List
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    score: float  # Score en centipawns
    best_move: str  # Meilleur coup en notation UCI
    pv: List[str]  # Ligne principale
    mate_in: Optional[int] = None  # Nombre de coups avant mat, si applicable

class ChessAnalyzer:
    def __init__(self, stockfish_path: Optional[str] = None):
        """
        Initialise l'analyseur d'échecs avec Stockfish.
        
        Args:
            stockfish_path: Chemin vers l'exécutable Stockfish.
                          Si None, tentera de trouver Stockfish automatiquement.
        """
        if stockfish_path is None:
            stockfish_path = self._find_stockfish()
        
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
            logger.info(f"Moteur Stockfish initialisé : {stockfish_path}")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Stockfish : {str(e)}")
            self.engine = None
    
    def _find_stockfish(self) -> str:
        """Trouve le chemin de Stockfish selon le système d'exploitation"""
        system = platform.system().lower()
        
        if system == "windows":
            # Cherche dans le dossier engines/
            local_path = os.path.join("engines", "stockfish", "stockfish-windows-x86-64.exe")
            if os.path.exists(local_path):
                return local_path
            
            # Cherche dans PATH
            return "stockfish.exe"
            
        elif system == "linux":
            # Cherche dans le dossier engines/
            local_path = os.path.join("engines", "stockfish", "stockfish-linux-x86-64")
            if os.path.exists(local_path):
                return local_path
            
            # Cherche dans les emplacements standards
            for path in ["/usr/local/bin/stockfish", "/usr/bin/stockfish"]:
                if os.path.exists(path):
                    return path
            
            return "stockfish"
            
        elif system == "darwin":  # macOS
            # Cherche dans le dossier engines/
            local_path = os.path.join("engines", "stockfish", "stockfish-macos-x86-64")
            if os.path.exists(local_path):
                return local_path
            
            # Cherche dans les emplacements standards
            for path in ["/usr/local/bin/stockfish", "/opt/homebrew/bin/stockfish"]:
                if os.path.exists(path):
                    return path
            
            return "stockfish"
        
        else:
            raise ValueError(f"Système d'exploitation non supporté : {system}")
    
    def analyze_position(self, fen: str, depth: int = 20, multipv: int = 3) -> List[AnalysisResult]:
        """
        Analyse une position d'échecs.
        
        Args:
            fen: Position en notation FEN
            depth: Profondeur d'analyse
            multipv: Nombre de variantes à calculer
            
        Returns:
            Liste des meilleurs coups avec leurs évaluations
        """
        if self.engine is None:
            logger.error("Moteur d'échecs non initialisé")
            return []
        
        try:
            board = chess.Board(fen)
            
            # Configure l'analyse
            limit = chess.engine.Limit(depth=depth)
            
            # Lance l'analyse
            info = self.engine.analyse(
                board,
                limit,
                multipv=multipv,
                info=chess.engine.INFO_ALL
            )
            
            # Traite les résultats
            results = []
            for pv in info:
                # Calcule le score en centipawns
                if 'score' in pv:
                    score = pv['score'].relative.score()
                    mate = pv['score'].relative.mate()
                else:
                    score = None
                    mate = None
                
                # Extrait la ligne principale
                if 'pv' in pv:
                    moves = [board.san(move) for move in pv['pv']]
                else:
                    moves = []
                
                # Extrait le meilleur coup
                if moves:
                    best_move = moves[0]
                else:
                    best_move = ""
                
                results.append(AnalysisResult(
                    score=score if score is not None else 0.0,
                    best_move=best_move,
                    pv=moves,
                    mate_in=mate
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse : {str(e)}")
            return []
    
    def get_position_summary(self, fen: str) -> str:
        """
        Génère un résumé en langage naturel de la position.
        
        Args:
            fen: Position en notation FEN
            
        Returns:
            Description de la position
        """
        try:
            # Analyse la position
            results = self.analyze_position(fen, depth=18, multipv=1)
            if not results:
                return "Impossible d'analyser la position."
            
            result = results[0]
            
            # Détermine l'avantage
            if result.mate_in is not None:
                if result.mate_in > 0:
                    advantage = f"Mat en {result.mate_in} coup{'s' if result.mate_in > 1 else ''}"
                else:
                    advantage = f"Mat en {-result.mate_in} coup{'s' if -result.mate_in > 1 else ''}"
            else:
                score = result.score / 100.0  # Convertit en pions
                if abs(score) < 0.5:
                    advantage = "Position égale"
                else:
                    color = "blancs" if score > 0 else "noirs"
                    advantage = f"Avantage {color} de {abs(score):.1f} pions"
            
            # Suggère le meilleur coup
            suggestion = f"Meilleur coup : {result.best_move}"
            
            # Combine le résumé
            return f"{advantage}. {suggestion}."
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du résumé : {str(e)}")
            return "Impossible de générer un résumé de la position."
    
    def __del__(self):
        """Ferme proprement le moteur"""
        if hasattr(self, 'engine') and self.engine:
            try:
                self.engine.quit()
            except:
                pass
