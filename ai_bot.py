# ai_bot.py
import random

def get_ai_move(board):
    """Basit bir AI: Önce boş yerleri bulur, rastgele seçer."""
    # İleride buraya Minimax algoritması ekleyerek yenilmez yapabiliriz.
    
    empty_cells = [i for i, x in enumerate(board) if x is None]
    
    if len(empty_cells) > 0:
        return random.choice(empty_cells)
    return None