# network_manager.py
import socket
import threading
import pickle
from constants import PORT

class NetworkManager:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = None
        self.conn = None # Sunucu ise bağlı olan istemci
        self.role = None # 'SERVER' veya 'CLIENT'
        self.connected = False
        self.received_data = None # Ana döngünün okuyacağı veri

    def host_game(self):
        """Sunucu olur ve bağlantı bekler."""
        self.role = 'SERVER'
        self.client.bind(('0.0.0.0', PORT))
        self.client.listen(1)
        print("Sunucu başlatıldı, bağlantı bekleniyor...")
        
        # Bağlantıyı kabul etme işlemini thread içinde yap (Bloklamasın)
        t = threading.Thread(target=self._accept_connection)
        t.daemon = True
        t.start()

    def _accept_connection(self):
        try:
            self.conn, self.addr = self.client.accept()
            self.connected = True
            print(f"Bağlandı: {self.addr}")
            # Veri dinlemeye başla
            threading.Thread(target=self._listen, args=(self.conn,)).start()
        except Exception as e:
            print(f"Bağlantı hatası: {e}")

    def connect_to_game(self, ip):
        """İstemci olur ve sunucuya bağlanır."""
        self.role = 'CLIENT'
        try:
            self.client.connect((ip, PORT))
            self.connected = True
            # Sunucu yerine 'client' soketini dinle
            threading.Thread(target=self._listen, args=(self.client,)).start()
            return True
        except Exception as e:
            print(f"Bağlantı başarısız: {e}")
            return False

    def _listen(self, connection):
        """Sürekli veri dinler."""
        while True:
            try:
                data = connection.recv(2048)
                if not data:
                    break
                self.received_data = pickle.loads(data)
            except:
                break
        self.connected = False
        print("Bağlantı koptu.")

    def send(self, data):
        """Veri gönderir (Hamle indeksi veya 'RESET')."""
        try:
            target = self.conn if self.role == 'SERVER' else self.client
            if target:
                target.send(pickle.dumps(data))
        except Exception as e:
            print(f"Gönderme hatası: {e}")

    def get_data(self):
        """Gelen veriyi okur ve kuyruğu temizler."""
        data = self.received_data
        self.received_data = None
        return data