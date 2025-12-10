# game_engine.py
class GameEngine:
    def __init__(self):
        self.board = [None] * 9
        self.current_player = 'X'
        self.winner = None
        self.game_over = False

    def reset(self):
        self.board = [None] * 9
        self.current_player = 'X'
        self.winner = None
        self.game_over = False

    def make_move(self, index, player=None):
        """Hamle yapar ve başarılıysa True döner."""
        if self.board[index] is None and not self.game_over:
            p = player if player else self.current_player
            if p != self.current_player:
                return False

            self.board[index] = p
            self.check_winner()
            if not self.game_over:
                self.switch_turn()
            return True
        return False

    def force_loss(self, loser_player):
        """Bir oyuncuyu (süre aşımı nedeniyle) kaybetmiş sayar."""
        if not self.game_over:
            self.winner = 'O' if loser_player == 'X' else 'X'
            self.game_over = True

    def switch_turn(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def check_winner(self):
        wins = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in wins:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                self.winner = self.board[a]
                self.game_over = True
                return
        if None not in self.board:
            self.winner = "Draw"
            self.game_over = True