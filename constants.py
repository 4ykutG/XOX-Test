# constants.py

# Ekran Ayarları
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 650 # Süre çubuğu için biraz yer açtık
BOARD_SIZE = 3
CELL_SIZE = SCREEN_WIDTH // BOARD_SIZE
GAME_AREA_TOP = 50 # Oyun alanı üstten 50px aşağıda başlayacak (süre çubuğu için)

# Oyun Ayarları
TURN_TIME_LIMIT = 10000  # Milisaniye cinsinden (10 saniye)

# Renk Paleti (Modern Dark Theme)
BG_TOP_COLOR = (20, 30, 48)      # Arka plan üst renk (Koyu Mavi)
BG_BOTTOM_COLOR = (36, 59, 85)   # Arka plan alt renk (Daha açık mavi)
GRID_COLOR = (50, 200, 255)      # Neon Mavisi Çizgiler
GRID_GLOW = (50, 200, 255, 100)  # Çizgi Parlaması (Yarı saydam)

# Sembol Renkleri
CIRCLE_COLOR = (255, 70, 70)     # 'O' Rengi (Neon Kırmızı)
CIRCLE_SHADOW = (150, 30, 30)    # 'O' Gölgesi
CROSS_COLOR = (70, 255, 70)      # 'X' Rengi (Neon Yeşil)
CROSS_SHADOW = (30, 150, 30)     # 'X' Gölgesi

# Arayüz Renkleri
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (40, 60, 90)
BUTTON_HOVER = (60, 90, 140)
BUTTON_BORDER = (100, 150, 200)
TIMER_BAR_COLOR = (255, 200, 0)  # Süre çubuğu rengi (Sarı/Turuncu)
TIMER_BG_COLOR = (40, 40, 40)

# Ağ Ayarları
DEFAULT_IP = '127.0.0.1'
PORT = 5555