# server.py (Nihai Sürüm: Global Hata Düzeltildi, Skor, Tekrar Oynama Desteği)

import socket
import sys
import threading
import time
from game_logic import initialize_board, check_win, check_draw
from utils import serialize_data, deserialize_data, HOST, PORT

# Global oyun durumu
game_board = initialize_board()
turn = 'X'
game_running = True
player_connections = {} # {'X': conn_obj, 'O': conn_obj}
connection_count = 0
scores = {'X': 0, 'O': 0} 
game_lock = threading.Lock() 

def send_update_to_all(status_msg, reset_board=False):
    """Tüm bağlı istemcilere güncel tahta durumunu, skoru ve sırayı gönderir."""
    global game_board, turn, scores

    if reset_board:
        game_board = initialize_board() # Tahtayı sıfırla
        turn = 'X' # Oyuna her zaman X başlasın

    update_data = {
        'board': game_board,
        'status': status_msg,
        'turn': turn,
        'scores': scores,
        'game_id': time.time()
    }
    
    serialized_data = serialize_data(update_data)
    
    for symbol, conn in player_connections.copy().items():
        try:
            conn.send(serialized_data)
        except:
            print(f"[HATA] {symbol} oyuncusuna veri gönderilemedi. Bağlantı kopmuş olabilir.")

# -----------------------------------------------------------
# HANDLE CLIENT FONKSİYONU BAŞLANGICI
# Global değişkenler burada tanımlanarak SyntaxError hatası düzeltilmiştir.
# -----------------------------------------------------------
def handle_client(conn, addr, player_symbol):
    """Her bir istemci bağlantısı için çalışan iş parçacığı (thread)."""
    # Global değişkenleri fonksiyonun en başında tanımla
    global game_board, turn, connection_count, scores 
    
    print(f"\n[BAĞLANTI] {addr} bağlandı, sembolü: {player_symbol}")
    
    # 1. İstemciye sembolünü ve başlangıç durumunu gönder
    try:
        initial_message = {
            'board': game_board,
            'status': 'WAITING' if connection_count < 2 else 'PLAYING',
            'turn': turn,
            'symbol': player_symbol,
            'scores': scores
        }
        conn.send(serialize_data(initial_message))
        
        while True:
            try:
                # İstemciden veri (Hamle indisi veya RESTART komutu) bekle
                conn.settimeout(0.5) 
                data = conn.recv(1024)
            except socket.timeout:
                continue 
            
            if not data:
                print(f"[HATA] {player_symbol} bağlantısı kesildi.")
                break
                
            client_data = deserialize_data(data)
            
            with game_lock:
            
                # 2. Yenileme Komutunu İşleme
                if client_data == "RESTART":
                    if turn == 'END_GAME':
                        print("[SERVER] Oyuncudan yenileme komutu geldi. Yeni tur başlıyor.")
                        send_update_to_all("PLAYING", reset_board=True)
                        # turn zaten X olarak ayarlandı, devam et
                        continue
                    else:
                        print("[SERVER] Yenileme komutu oyun bitmeden geldi, yok sayılıyor.")
                        continue
                        
                # 3. Hamleyi İşleme (Gelen veri bir tamsayı (indis) ise)
                elif isinstance(client_data, int) and turn == player_symbol:
                    move_index = client_data 
                    
                    if 0 <= move_index <= 8 and game_board[move_index] == ' ':
                        game_board[move_index] = player_symbol
                        
                        # Durum Kontrolü
                        if check_win(game_board, player_symbol):
                            status_msg = f"WINNER: {player_symbol}"
                            scores[player_symbol] += 1
                            print(f"[TUR SONU] {player_symbol} kazandı! Skorlar: X:{scores['X']} O:{scores['O']}")
                            turn = 'END_GAME'
                            
                        elif check_draw(game_board):
                            status_msg = "DRAW"
                            print("[TUR SONU] Beraberlik!")
                            turn = 'END_GAME'
                            
                        else:
                            status_msg = "PLAYING"
                            # Sıra Değiştirme
                            turn = 'O' if player_symbol == 'X' else 'X'
                        
                        # Güncel durumu her iki istemciye de gönder
                        send_update_to_all(status_msg)
                    
                    else:
                        print(f"[HATA] {player_symbol} geçersiz hamle yaptı.")
                        send_update_to_all("PLAYING")
                
                elif turn != player_symbol:
                    print(f"[UYARI] {player_symbol} sırası değilken hamle yapmaya çalıştı.")
                    send_update_to_all("PLAYING")
                    
                else:
                    print(f"[UYARI] Tanınmayan veri formatı geldi: {client_data}")

    except Exception as e:
        print(f"[İSTEMCİ HATA] {player_symbol} (Addr: {addr}) hata ile kapandı: {e}")
        
# server.py (handle_client fonksiyonu içindeki finally bloğu - DÜZELTİLMİŞ)

    finally:
        with game_lock:
            # ... (Bu kısım aynı kalır)

            connection_count -= 1 
            
            print(f"[BİTTİ] {addr} bağlantısı kapatıldı. Kalan bağlantı: {connection_count}")
            
            # Eğer bir oyuncu ayrılırsa, oyunu sonlandır ve diğerine bildir.
            if connection_count < 2:
                print("[SUNUCU] Yeterli oyuncu yok. Yeni bağlantı bekleniyor...")
                send_update_to_all("DISCONNECTED") 
                
                # HATA VEREN SATIR KALDIRILDI! 
                # global game_board, scores, turn # BU SATIR SİLİNMELİ
                
                game_board = initialize_board() 
                scores = {'X': 0, 'O': 0} 
                turn = 'X' 
# -----------------------------------------------------------
# HANDLE CLIENT FONKSİYONU SONU
# -----------------------------------------------------------
# -----------------------------------------------------------
# HANDLE CLIENT FONKSİYONU SONU
# -----------------------------------------------------------

# -----------------------------------------------------------
# START SERVER FONKSİYONU BAŞLANGICI
# -----------------------------------------------------------
def start_server():
    """Ana sunucu döngüsü, iki oyuncuyu bağlayana kadar bekler."""
    # Global tanımlamalar
    global connection_count, player_connections, game_board, scores 
    
    server_socket = None
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(2)
        
        print(f"Sunucu başlatıldı: {HOST}:{PORT}")
        print("İki istemci bağlantısı bekleniyor...")
        
        symbols = ['X', 'O']
        
        while True:
            conn, addr = server_socket.accept()
            
            with game_lock:
                if connection_count >= 2:
                    print(f"[REDDEDİLDİ] Üçüncü bağlantı {addr} reddedildi.")
                    conn.send(serialize_data("FULL"))
                    conn.close()
                    continue

                symbol = symbols[connection_count]
                player_connections[symbol] = conn
                connection_count += 1
            
            thread = threading.Thread(target=handle_client, args=(conn, addr, symbol))
            thread.daemon = True
            thread.start()
            
            print(f"Oyuncu {symbol} bağlandı. Toplam {connection_count}/2.")

            if connection_count == 2:
                 print("\n*** İKİ OYUNCU TAMAMLANDI. OYUN BAŞLADI! (X Başlıyor) ***")
                 send_update_to_all("PLAYING")
                 
    except socket.error as e:
        print(f"[KRİTİK HATA] Soket hatası: {e}")
        sys.exit(1)
    finally:
        if server_socket:
            server_socket.close()
            print("\n[SUNUCU KAPATILDI]")

if __name__ == '__main__':
    start_server()