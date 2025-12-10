# client.py
import socket
import sys
from game_logic import print_board
from utils import serialize_data, deserialize_data, HOST, PORT

def start_client():
    """İstemci soketini başlatır, sunucuya bağlanır ve oyun döngüsünü başlatır."""
    
    # Sunucunun IP adresi ve portu (utils.py'den çekiliyor)
    server_address = (HOST, PORT)
    client_socket = None
    
    try:
        # İstemci soketini oluştur
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[BAĞLANIYOR] Sunucuya bağlanılıyor: {HOST}:{PORT}")
        
        # Sunucuya bağlan
        client_socket.connect(server_address)
        print("[BAĞLANTI BAŞARILI] Sunucuya bağlandı.")
        
        # Sunucudan ilk karşılama mesajını al
        initial_data = client_socket.recv(1024)
        if initial_data:
            print(f"[SUNUCU] {deserialize_data(initial_data)}")
        
        player_symbol = 'O' # Client, server'da 'O' olarak atanmıştı

        while True:
            # 1. Sunucudan oyun durumunu al
            data = client_socket.recv(4096) # 4096 byte'a kadar veri al
            if not data:
                print("[HATA] Sunucudan veri alınamadı, bağlantı kesildi.")
                break
            
            game_state = deserialize_data(data)
            board = game_state['board']
            status = game_state['status']
            current_turn = game_state['turn']

            print_board(board)

            # 2. Oyun Durumu Kontrolü (Kazanma/Beraberlik)
            if status != 'PLAYING':
                if status == 'DRAW':
                    print("\n*** OYUN SONU: Beraberlik! ***")
                elif status.startswith('WINNER'):
                    winner = status.split(': ')[1]
                    print(f"\n*** OYUN SONU: {winner} Kazandı! ***")
                break # Oyun bitti, döngüden çık

            # 3. Hamle Sırası Kontrolü
            if current_turn == player_symbol:
                # Kendi sıramız, hamle yap
                while True:
                    try:
                        # Oyuncudan 1-9 arası hamle al ve 0-8 indisine çevir
                        move = input(f"Senin sıran ({player_symbol}). Hamleni gir (1-9): ")
                        move_index = int(move) - 1
                        
                        # İndis geçerli mi ve alan boş mu (Basit yerel kontrol)
                        # Daha kesin kontrol server'da yapılacak, ama burada kullanıcı deneyimini iyileştiriyoruz.
                        if 0 <= move_index <= 8 and board[move_index] == ' ':
                            
                            # Hamleyi sunucuya gönder
                            client_socket.send(serialize_data(move_index))
                            print(f"[GÖNDERİLDİ] Hamle: {move_index + 1}. Sunucu onayı bekleniyor...")
                            break
                        else:
                            print("Geçersiz hamle. Lütfen boş bir alanın 1-9 arası numarasını girin.")
                    except ValueError:
                        print("Hatalı giriş. Lütfen bir sayı girin.")
            
            else:
                # Rakibin sırası, bekle
                print(f"[BEKLEME] Rakibin ({current_turn}) hamlesi bekleniyor...")
                # client.recv() döngünün başına dönerek yeni tahta durumunu alacak.

    except ConnectionRefusedError:
        print("[HATA] Sunucuya bağlanılamadı. Sunucunun çalışıp çalışmadığını ve IP adresinin doğru olup olmadığını kontrol edin.")
    except socket.error as e:
        print(f"[KRİTİK HATA] Soket hatası: {e}")
    except Exception as e:
        print(f"[BEKLENMEYEN HATA] {e}")
    finally:
        if client_socket:
            client_socket.close()
            print("[BİTTİ] Bağlantı kapatıldı.")

if __name__ == '__main__':
    start_client()