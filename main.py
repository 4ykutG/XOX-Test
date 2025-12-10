# main.py
import pygame
import sys
from constants import *
from game_engine import GameEngine
from ai_bot import get_ai_move
from network_manager import NetworkManager

# Pygame Başlatma
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("XOX - Ultimate Pygame Edition")
font = pygame.font.SysFont('Arial', 40, bold=True)

class XOXGame:
    def __init__(self):
        self.engine = GameEngine()
        self.network = NetworkManager()
        self.state = "MENU" # MENU, LOCAL, AI, LAN_LOBBY, LAN_GAME
        self.my_lan_symbol = None # LAN'da ben X miyim O muyum?

    def draw_grid(self):
        screen.fill(BG_COLOR)
        # Yatay Çizgiler
        pygame.draw.line(screen, LINE_COLOR, (0, CELL_SIZE), (SCREEN_WIDTH, CELL_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, 2 * CELL_SIZE), (SCREEN_WIDTH, 2 * CELL_SIZE), LINE_WIDTH)
        # Dikey Çizgiler
        pygame.draw.line(screen, LINE_COLOR, (CELL_SIZE, 0), (CELL_SIZE, SCREEN_HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (2 * CELL_SIZE, 0), (2 * CELL_SIZE, SCREEN_HEIGHT), LINE_WIDTH)

    def draw_figures(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                index = row * 3 + col
                if self.engine.board[index] == 'O':
                    pygame.draw.circle(screen, CIRCLE_COLOR, (int(col * CELL_SIZE + CELL_SIZE / 2), int(row * CELL_SIZE + CELL_SIZE / 2)), 60, 15)
                elif self.engine.board[index] == 'X':
                    # X çizimi
                    start_desc = (col * CELL_SIZE + 55, row * CELL_SIZE + 55)
                    end_desc = (col * CELL_SIZE + CELL_SIZE - 55, row * CELL_SIZE + CELL_SIZE - 55)
                    pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, 25)
                    start_asc = (col * CELL_SIZE + 55, row * CELL_SIZE + CELL_SIZE - 55)
                    end_asc = (col * CELL_SIZE + CELL_SIZE - 55, row * CELL_SIZE + 55)
                    pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, 25)

    def draw_status(self):
        if self.engine.game_over:
            if self.engine.winner == "Draw":
                text = "Beraberlik! (R ile Yenile)"
            else:
                text = f"Kazanan: {self.engine.winner} (R ile Yenile)"
        else:
            if self.state == "LAN_GAME":
                text = f"Sen: {self.my_lan_symbol} | Sıra: {self.engine.current_player}"
            else:
                text = f"Sıra: {self.engine.current_player}"
        
        lbl = font.render(text, True, TEXT_COLOR)
        # Metni ekranın altına ortala
        screen.blit(lbl, (SCREEN_WIDTH//2 - lbl.get_width()//2, SCREEN_HEIGHT - 40))

    def draw_menu(self):
        screen.fill(BUTTON_COLOR)
        title = font.render("XOX OYUNU", True, (28, 170, 156))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        # Butonlar
        self.draw_button("1. Bilgisayara Karşı", 200, "AI")
        self.draw_button("2. Yerel (2 Kişi)", 300, "LOCAL")
        self.draw_button("3. Ağ Oyunu (LAN)", 400, "LAN_LOBBY")

    def draw_button(self, text, y, action_code):
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(100, y, 400, 60)
        
        color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else (50, 50, 50)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        
        lbl = font.render(text, True, TEXT_COLOR)
        screen.blit(lbl, (SCREEN_WIDTH//2 - lbl.get_width()//2, y + 10))
        
        # Tıklama kontrolü burada yapılmaz, event loop'ta yapılır
        return rect

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and not self.engine.game_over:
                    if self.state == "MENU":
                        self.handle_menu_click(event.pos)
                    elif self.state in ["LOCAL", "AI", "LAN_GAME"]:
                        self.handle_game_click(event.pos)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.engine.game_over:
                        self.restart_game()
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                        self.engine.reset()

            # --- GÜNCELLEMELER ---
            if self.state == "MENU":
                self.draw_menu()

            elif self.state == "LAN_LOBBY":
                # Basit bir LAN kurulum ekranı (Konsol girdisi kullanacağız kolaylık için)
                screen.fill(BUTTON_COLOR)
                msg = font.render("Konsola bakin...", True, TEXT_COLOR)
                screen.blit(msg, (50, 250))
                pygame.display.update()
                
                print("\n--- LAN MODU SEÇİMİ ---")
                print("1. Oyunu Kur (Host - X)")
                print("2. Oyuna Katıl (Client - O)")
                choice = input("Seçiminiz (1/2): ")
                
                if choice == '1':
                    self.network.host_game()
                    self.my_lan_symbol = 'X'
                    self.state = "LAN_GAME"
                    self.engine.reset()
                elif choice == '2':
                    ip = input(f"Sunucu IP (Varsayılan {DEFAULT_IP}): ") or DEFAULT_IP
                    if self.network.connect_to_game(ip):
                        self.my_lan_symbol = 'O'
                        self.state = "LAN_GAME"
                        self.engine.reset()
                    else:
                        self.state = "MENU"

            elif self.state in ["LOCAL", "AI", "LAN_GAME"]:
                self.draw_grid()
                self.draw_figures()
                self.draw_status()

                # AI Hamlesi
                if self.state == "AI" and self.engine.current_player == 'O' and not self.engine.game_over:
                    pygame.display.update()
                    pygame.time.delay(500) # Düşünme efekti
                    move = get_ai_move(self.engine.board)
                    if move is not None:
                        self.engine.make_move(move)

                # LAN Veri Kontrolü
                if self.state == "LAN_GAME":
                    data = self.network.get_data()
                    if data is not None:
                        if data == "RESET":
                            self.engine.reset()
                        elif isinstance(data, int):
                            # Gelen hamleyi uygula
                            # Ağdan gelen hamle rakibin hamlesidir
                            opponent = 'O' if self.my_lan_symbol == 'X' else 'X'
                            self.engine.make_move(data, player=opponent)

            pygame.display.update()

    def handle_menu_click(self, pos):
        # Buton alanları (Hardcoded koordinatlar main draw ile aynı olmalı)
        if 100 <= pos[0] <= 500:
            if 200 <= pos[1] <= 260:
                self.state = "AI"
                self.engine.reset()
            elif 300 <= pos[1] <= 360:
                self.state = "LOCAL"
                self.engine.reset()
            elif 400 <= pos[1] <= 460:
                self.state = "LAN_LOBBY"

    def handle_game_click(self, pos):
        # Tıklanan koordinatı grid indeksine çevir
        clicked_col = int(pos[0] // CELL_SIZE)
        clicked_row = int(pos[1] // CELL_SIZE)
        index = clicked_row * 3 + clicked_col

        # Modlara göre hamle izni
        if self.state == "LOCAL":
            self.engine.make_move(index)
        
        elif self.state == "AI":
            # Sadece X iken (insan) tıklamaya izin ver
            if self.engine.current_player == 'X':
                self.engine.make_move(index)
        
        elif self.state == "LAN_GAME":
            # Sadece kendi sıramızsa tıklamaya izin ver
            if self.engine.current_player == self.my_lan_symbol:
                if self.engine.make_move(index, player=self.my_lan_symbol):
                    # Hamle geçerliyse ağa gönder
                    self.network.send(index)

    def restart_game(self):
        self.engine.reset()
        if self.state == "LAN_GAME":
            self.network.send("RESET")

if __name__ == "__main__":
    game = XOXGame()
    game.run()