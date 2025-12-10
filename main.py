# main.py
import pygame
import sys
import threading # LAN bekleme kontrolü için gerekli
from constants import *
from game_engine import GameEngine
from ai_bot import get_ai_move
from network_manager import NetworkManager

# Pygame Başlatma
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("XOX - Neon Edition")

# Font Ayarları
try:
    font_large = pygame.font.Font("arialbd.ttf", 60)
    font_med = pygame.font.Font("arial.ttf", 32)
    font_small = pygame.font.Font("arial.ttf", 24)
except:
    font_large = pygame.font.SysFont('Arial', 60, bold=True)
    font_med = pygame.font.SysFont('Arial', 32)
    font_small = pygame.font.SysFont('Arial', 24)

class XOXGame:
    def __init__(self):
        self.engine = GameEngine()
        self.network = NetworkManager()
        self.state = "MENU" 
        # State Listesi: MENU, LOCAL, AI, LAN_LOBBY, LAN_WAITING (Yeni), LAN_GAME
        
        self.my_lan_symbol = None
        
        # Zamanlayıcı Değişkenleri
        self.turn_start_time = 0
        self.time_left = TURN_TIME_LIMIT

    # --- YARDIMCI ÇİZİM FONKSİYONLARI ---
    def draw_gradient_bg(self):
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = BG_TOP_COLOR[0] * (1 - ratio) + BG_BOTTOM_COLOR[0] * ratio
            g = BG_TOP_COLOR[1] * (1 - ratio) + BG_BOTTOM_COLOR[1] * ratio
            b = BG_TOP_COLOR[2] * (1 - ratio) + BG_BOTTOM_COLOR[2] * ratio
            pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (SCREEN_WIDTH, y))

    def draw_shadowed_text(self, text, font, color, shadow_color, pos, center=True):
        shadow_surf = font.render(text, True, shadow_color)
        text_surf = font.render(text, True, color)
        x, y = pos
        if center:
            x -= text_surf.get_width() // 2
            y -= text_surf.get_height() // 2
        screen.blit(shadow_surf, (x + 3, y + 3))
        screen.blit(text_surf, (x, y))

    def draw_fancy_grid(self):
        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Yatay Parlamalar
        pygame.draw.line(glow_surface, GRID_GLOW, (0, CELL_SIZE + GAME_AREA_TOP), (SCREEN_WIDTH, CELL_SIZE + GAME_AREA_TOP), LINE_WIDTH + 6)
        pygame.draw.line(glow_surface, GRID_GLOW, (0, 2 * CELL_SIZE + GAME_AREA_TOP), (SCREEN_WIDTH, 2 * CELL_SIZE + GAME_AREA_TOP), LINE_WIDTH + 6)
        # Dikey Parlamalar
        pygame.draw.line(glow_surface, GRID_GLOW, (CELL_SIZE, GAME_AREA_TOP), (CELL_SIZE, SCREEN_HEIGHT), LINE_WIDTH + 6)
        pygame.draw.line(glow_surface, GRID_GLOW, (2 * CELL_SIZE, GAME_AREA_TOP), (2 * CELL_SIZE, SCREEN_HEIGHT), LINE_WIDTH + 6)
        screen.blit(glow_surface, (0,0))

        # Ana Çizgiler
        pygame.draw.line(screen, GRID_COLOR, (0, CELL_SIZE + GAME_AREA_TOP), (SCREEN_WIDTH, CELL_SIZE + GAME_AREA_TOP), LINE_WIDTH)
        pygame.draw.line(screen, GRID_COLOR, (0, 2 * CELL_SIZE + GAME_AREA_TOP), (SCREEN_WIDTH, 2 * CELL_SIZE + GAME_AREA_TOP), LINE_WIDTH)
        pygame.draw.line(screen, GRID_COLOR, (CELL_SIZE, GAME_AREA_TOP), (CELL_SIZE, SCREEN_HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, GRID_COLOR, (2 * CELL_SIZE, GAME_AREA_TOP), (2 * CELL_SIZE, SCREEN_HEIGHT), LINE_WIDTH)

    def draw_figures(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                index = row * 3 + col
                center_x = int(col * CELL_SIZE + CELL_SIZE / 2)
                center_y = int(row * CELL_SIZE + CELL_SIZE / 2) + GAME_AREA_TOP

                if self.engine.board[index] == 'O':
                    pygame.draw.circle(screen, CIRCLE_SHADOW, (center_x + 4, center_y + 4), 60, SYMBOL_WIDTH)
                    pygame.draw.circle(screen, CIRCLE_COLOR, (center_x, center_y), 60, SYMBOL_WIDTH)
                elif self.engine.board[index] == 'X':
                    offset = 55
                    p1 = (col * CELL_SIZE + offset, row * CELL_SIZE + offset + GAME_AREA_TOP)
                    p2 = (col * CELL_SIZE + CELL_SIZE - offset, row * CELL_SIZE + CELL_SIZE - offset + GAME_AREA_TOP)
                    p3 = (col * CELL_SIZE + offset, row * CELL_SIZE + CELL_SIZE - offset + GAME_AREA_TOP)
                    p4 = (col * CELL_SIZE + CELL_SIZE - offset, row * CELL_SIZE + offset + GAME_AREA_TOP)
                    
                    pygame.draw.line(screen, CROSS_SHADOW, (p1[0]+4, p1[1]+4), (p2[0]+4, p2[1]+4), 25)
                    pygame.draw.line(screen, CROSS_SHADOW, (p3[0]+4, p3[1]+4), (p4[0]+4, p4[1]+4), 25)
                    pygame.draw.line(screen, CROSS_COLOR, p1, p2, 25)
                    pygame.draw.line(screen, CROSS_COLOR, p3, p4, 25)

    def draw_timer_bar(self):
        if self.engine.game_over or self.state == "MENU": return
        pygame.draw.rect(screen, TIMER_BG_COLOR, (0, 0, SCREEN_WIDTH, GAME_AREA_TOP))
        bar_width = int(SCREEN_WIDTH * (self.time_left / TURN_TIME_LIMIT))
        color = TIMER_BAR_COLOR
        if self.time_left < 3000: color = (255, 50, 50)
        elif self.time_left < 6000: color = (255, 150, 0)
        pygame.draw.rect(screen, color, (0, 0, bar_width, GAME_AREA_TOP - 5))
        seconds = self.time_left // 1000
        time_text = font_small.render(f"{seconds + 1} sn", True, TEXT_COLOR)
        screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, 10))

    def draw_styled_button(self, text, x, y, width, height, action_code):
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, width, height)
        is_hovered = rect.collidepoint(mouse_pos)
        bg_color = BUTTON_HOVER if is_hovered else BUTTON_COLOR
        border_color = BUTTON_BORDER if is_hovered else (60, 80, 110)
        pygame.draw.rect(screen, (20, 20, 30), (x+4, y+4, width, height), border_radius=15)
        pygame.draw.rect(screen, bg_color, rect, border_radius=15)
        pygame.draw.rect(screen, border_color, rect, width=3, border_radius=15)
        text_color = TEXT_COLOR if is_hovered else (200, 200, 200)
        lbl = font_med.render(text, True, text_color)
        screen.blit(lbl, (x + width//2 - lbl.get_width()//2, y + height//2 - lbl.get_height()//2))
        return rect

    # --- OYUN MANTIĞI ---
    def reset_game_state(self):
        self.engine.reset()
        self.reset_timer()

    def reset_timer(self):
        self.turn_start_time = pygame.time.get_ticks()
        self.time_left = TURN_TIME_LIMIT

    def update_timer(self):
        if self.engine.game_over or self.state == "MENU" or self.state == "LAN_WAITING": return
        
        should_tick = False
        if self.state == "LOCAL":
            should_tick = True
        elif self.state == "AI" and self.engine.current_player == 'X':
            should_tick = True
        elif self.state == "LAN_GAME" and self.engine.current_player == self.my_lan_symbol:
            should_tick = True
            
        if should_tick:
            current_time = pygame.time.get_ticks()
            time_elapsed = current_time - self.turn_start_time
            self.time_left = max(0, TURN_TIME_LIMIT - time_elapsed)

            if self.time_left == 0:
                print("Süre Doldu!")
                loser = self.engine.current_player
                self.engine.force_loss(loser)
                if self.state == "LAN_GAME":
                    self.network.send("TIMEOUT")

    # --- ÇİZİMLER ---
    def draw_game_interface(self):
        self.draw_gradient_bg()
        self.draw_timer_bar()
        self.draw_fancy_grid()
        self.draw_figures()
        self.draw_status()

    def draw_status(self):
        status_text = ""
        color = TEXT_COLOR
        if self.engine.game_over:
            if self.engine.winner == "Draw":
                status_text = "Beraberlik! (Yenilemek için R)"
            else:
                status_text = f"Kazanan: {self.engine.winner}! (Yenilemek için R)"
                color = CROSS_COLOR if self.engine.winner == 'X' else CIRCLE_COLOR
        else:
            turn_player = self.engine.current_player
            turn_color = CROSS_COLOR if turn_player == 'X' else CIRCLE_COLOR
            if self.state == "LAN_GAME":
                status_text = f"Sen: {self.my_lan_symbol}  |  Sıra: {turn_player}"
            else:
                status_text = f"Sıra: {turn_player}"
            
            self.draw_shadowed_text(status_text, font_med, turn_color, (0,0,0), (SCREEN_WIDTH//2, SCREEN_HEIGHT - 40))
            return
        self.draw_shadowed_text(status_text, font_med, color, (0,0,0), (SCREEN_WIDTH//2, SCREEN_HEIGHT - 40))

    def draw_menu(self):
        self.draw_gradient_bg()
        self.draw_shadowed_text("NEON XOX", font_large, GRID_COLOR, (0,0,0), (SCREEN_WIDTH//2, 100))
        self.draw_styled_button("Bilgisayara Karşı", 100, 200, 400, 70, "AI")
        self.draw_styled_button("Yerel (2 Kişi)", 100, 300, 400, 70, "LOCAL")
        self.draw_styled_button("Ağ Oyunu (LAN)", 100, 400, 400, 70, "LAN_LOBBY")

    def run(self):
        clock = pygame.time.Clock()
        
        while True:
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and not self.engine.game_over:
                    if self.state == "MENU":
                        self.handle_menu_click(event.pos)
                    elif self.state in ["LOCAL", "AI", "LAN_GAME"]:
                        if event.pos[1] > GAME_AREA_TOP:
                            self.handle_game_click(event.pos)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.engine.game_over:
                        self.restart_game()
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                        self.reset_game_state()
                        if self.network.connected:
                            self.network.client.close()

            # --- GÜNCELLEMELER ---
            self.update_timer()

            if self.state == "MENU":
                self.draw_menu()

            elif self.state == "LAN_LOBBY":
                # Lobi Seçim Ekranı
                self.draw_gradient_bg()
                self.draw_shadowed_text("Lütfen Konsola Bakın...", font_med, TEXT_COLOR, (0,0,0), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                pygame.display.update()
                
                print("\n--- LAN MODU SEÇİMİ ---")
                print("1. Oyunu Kur (Host - X)")
                print("2. Oyuna Katıl (Client - O)")
                try:
                    choice = input("Seçiminiz (1/2): ")
                    if choice == '1':
                        self.network.host_game()
                        self.my_lan_symbol = 'X'
                        # DİREKT OYUNA GİRMEK YERİNE BEKLEME MODUNA ALIYORUZ
                        self.state = "LAN_WAITING" 
                        self.reset_game_state()
                    elif choice == '2':
                        ip = input(f"Sunucu IP (Varsayılan {DEFAULT_IP}): ") or DEFAULT_IP
                        if self.network.connect_to_game(ip):
                            self.my_lan_symbol = 'O'
                            self.state = "LAN_GAME"
                            self.reset_game_state()
                        else:
                            self.state = "MENU"
                except:
                    self.state = "MENU"

            # --- YENİ EKLENEN DURUM: BEKLEME EKRANI ---
            elif self.state == "LAN_WAITING":
                self.draw_gradient_bg()
                
                # Animasyonlu Bekleme Yazısı (Basit)
                dots = "." * (int(pygame.time.get_ticks() / 500) % 4)
                text = f"Rakip Bağlanması Bekleniyor{dots}"
                
                self.draw_shadowed_text(text, font_med, TEXT_COLOR, (0,0,0), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.draw_shadowed_text(f"IP: {DEFAULT_IP} (veya yerel IP)", font_small, GRID_COLOR, (0,0,0), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
                
                # Bağlantı Kontrolü
                if self.network.connected:
                    print("Rakip Bağlandı! Oyun Başlıyor.")
                    self.state = "LAN_GAME"
                    self.reset_game_state()

            elif self.state in ["LOCAL", "AI", "LAN_GAME"]:
                self.draw_game_interface()

                # AI Hamlesi
                if self.state == "AI" and self.engine.current_player == 'O' and not self.engine.game_over:
                    pygame.display.update()
                    pygame.time.delay(500)
                    move = get_ai_move(self.engine.board)
                    if move is not None:
                        self.engine.make_move(move)
                        self.reset_timer()

                # LAN Veri Kontrolü
                if self.state == "LAN_GAME":
                    data = self.network.get_data()
                    if data is not None:
                        if data == "RESET":
                            self.reset_game_state()
                        elif data == "TIMEOUT":
                            opponent = 'O' if self.my_lan_symbol == 'X' else 'X'
                            self.engine.force_loss(opponent)
                        elif isinstance(data, int):
                            opponent = 'O' if self.my_lan_symbol == 'X' else 'X'
                            if self.engine.make_move(data, player=opponent):
                                self.reset_timer()

            pygame.display.update()

    def handle_menu_click(self, pos):
        x, width, height = 100, 400, 70
        if x <= pos[0] <= x + width:
            if 200 <= pos[1] <= 270:
                self.state = "AI"
                self.reset_game_state()
            elif 300 <= pos[1] <= 370:
                self.state = "LOCAL"
                self.reset_game_state()
            elif 400 <= pos[1] <= 470:
                self.state = "LAN_LOBBY"

    def handle_game_click(self, pos):
        adj_y = pos[1] - GAME_AREA_TOP
        clicked_col = int(pos[0] // CELL_SIZE)
        clicked_row = int(adj_y // CELL_SIZE)
        index = clicked_row * 3 + clicked_col

        if index < 0 or index > 8: return

        move_made = False
        if self.state == "LOCAL":
            move_made = self.engine.make_move(index)
        elif self.state == "AI":
            if self.engine.current_player == 'X':
                move_made = self.engine.make_move(index)
        elif self.state == "LAN_GAME":
            if self.engine.current_player == self.my_lan_symbol:
                if self.engine.make_move(index, player=self.my_lan_symbol):
                    self.network.send(index)
                    move_made = True

        if move_made:
            self.reset_timer()

    def restart_game(self):
        self.reset_game_state()
        if self.state == "LAN_GAME":
            self.network.send("RESET")

if __name__ == "__main__":
    game = XOXGame()
    game.run()