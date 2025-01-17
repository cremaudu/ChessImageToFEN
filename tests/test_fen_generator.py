import pytest
from src.fen_generator import FENGenerator

def test_empty_board():
    pieces = ['empty'] * 64
    fen = FENGenerator.pieces_to_fen(pieces)
    assert fen == "8/8/8/8/8/8/8/8 w - - 0 1"
    assert FENGenerator.validate_fen(fen)

def test_starting_position():
    pieces = [
        'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',  # 8th rank
        'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',  # 7th rank
        'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty',  # 6th rank
        'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty',  # 5th rank
        'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty',  # 4th rank
        'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty',  # 3rd rank
        'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',  # 2nd rank
        'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'   # 1st rank
    ]
    fen = FENGenerator.pieces_to_fen(pieces)
    assert fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1"
    assert FENGenerator.validate_fen(fen)

def test_invalid_input():
    # Test avec une liste trop courte
    pieces = ['empty'] * 63  # 63 au lieu de 64
    fen = FENGenerator.pieces_to_fen(pieces)
    assert fen == "8/8/8/8/8/8/8/8 w - - 0 1"  # Devrait retourner un échiquier vide

def test_complex_position():
    pieces = [
        'empty', 'empty', 'k', 'empty', 'empty', 'b', 'n', 'r',
        'p', 'empty', 'p', 'empty', 'empty', 'p', 'p', 'p',
        'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty',
        'empty', 'p', 'empty', 'empty', 'P', 'empty', 'empty', 'empty',
        'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty',
        'empty', 'empty', 'N', 'empty', 'empty', 'empty', 'empty', 'empty',
        'P', 'P', 'P', 'B', 'empty', 'P', 'P', 'P',
        'R', 'empty', 'empty', 'empty', 'K', 'empty', 'empty', 'R'
    ]
    fen = FENGenerator.pieces_to_fen(pieces)
    assert FENGenerator.validate_fen(fen)
