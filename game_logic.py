# game_logic.py

def initialize_board():
    """Yeni bir boş 3x3 tahta oluşturur."""
    # Tahta, 0'dan 8'e kadar indislerle temsil edilir.
    # Her eleman ' ' (boş), 'X' veya 'O' olabilir.
    return [' '] * 9

def print_board(board):
    """Tahtayı konsolda kullanıcı dostu bir şekilde yazdırır."""
    print("\n--- XOX TAHTASI ---")
    print(f" {board[0]} | {board[1]} | {board[2]}    1 | 2 | 3")
    print("---|---|---  ---|---|---")
    print(f" {board[3]} | {board[4]} | {board[5]}    4 | 5 | 6")
    print("---|---|---  ---|---|---")
    print(f" {board[6]} | {board[7]} | {board[8]}    7 | 8 | 9")
    print("-------------------")
    # Sağ tarafta kullanıcının hamle yaparken kullanacağı indisler gösterilmiştir.

def is_valid_move(board, move_index):
    """
    Verilen indis geçerli bir hamle yeri midir? (0-8 aralığında ve boş olmalı)
    """
    if not (0 <= move_index <= 8):
        return False
    # Seçilen alan boşsa geçerlidir.
    return board[move_index] == ' '

def check_win(board, player):
    """Belirtilen oyuncu (X veya O) kazanmış mı kontrol eder."""
    # Kazanma ihtimalleri: Yatay, Dikey ve Çapraz.
    # Her bir eleman bir indis üçlüsüdür.
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Yatay
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Dikey
        (0, 4, 8), (2, 4, 6)             # Çapraz
    ]
    
    # 

    for combo in winning_combinations:
        # Üç indiste de oyuncunun sembolü varsa kazanmıştır.
        if (board[combo[0]] == player and
            board[combo[1]] == player and
            board[combo[2]] == player):
            return True
    return False

def check_draw(board):
    """Oyun tahtasında boş alan kalmadıysa ve kazanan yoksa beraberliktir."""
    # Eğer tahtada boşluk yoksa (' ' yoksa) ve kazanan yoksa.
    return ' ' not in board