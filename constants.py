# constants.py

# Ekran Ayarları
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BOARD_SIZE = 3
CELL_SIZE = SCREEN_WIDTH // BOARD_SIZE
LINE_WIDTH = 10
SYMBOL_WIDTH = 15

# Renkler (RGB)
BG_COLOR = (28, 170, 156)    # Turkuaz Arka Plan
LINE_COLOR = (23, 145, 135)  # Çizgi Rengi
CIRCLE_COLOR = (239, 231, 200) # 'O' Rengi (Krem)
CROSS_COLOR = (84, 84, 84)   # 'X' Rengi (Koyu Gri)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (20, 20, 20)
BUTTON_HOVER = (50, 50, 50)

# Ağ Ayarları
# LAN oynarken Sunucu olan bilgisayarın IP'sini buraya yazın veya konsoldan girin.
DEFAULT_IP = '127.0.0.1' 
PORT = 5555