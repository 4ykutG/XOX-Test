# network_manager.py
import socket
import threading
import pickle
from constants import PORT

class NetworkManager:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = None
        self.conn = None
        self.role = None
        self.connected = False
        self.received_data = None

    def host_game(self):
        self.role = 'SERVER'
        self.client.bind(('0.0.0.0', PORT))
        self.client.listen(1)
        print("Sunucu başlatıldı, bağlantı bekleniyor...")
        t = threading.Thread(target=self._accept_connection)
        t.daemon = True
        t.start()

    def _accept_connection(self):
        try:
            self.conn, self.addr = self.client.accept()
            self.connected = True
            print(f"Bağlandı: {self.addr}")
            threading.Thread(target=self._listen, args=(self.conn,)).start()
        except Exception as e:
            print(f"Bağlantı hatası: {e}")

    def connect_to_game(self, ip):
        self.role = 'CLIENT'
        try:
            self.client.connect((ip, PORT))
            self.connected = True
            threading.Thread(target=self._listen, args=(self.client,)).start()
            return True
        except Exception as e:
            print(f"Bağlantı başarısız: {e}")
            return False

    def _listen(self, connection):
        while True:
            try:
                data = connection.recv(2048)
                if not data:
                    break
                # Gelen veriyi işle
                self.received_data = pickle.loads(data)
            except:
                break
        self.connected = False
        print("Bağlantı koptu.")

    def send(self, data):
        """Veri gönderir (Hamle indeksi, 'RESET' veya 'TIMEOUT')."""
        try:
            target = self.conn if self.role == 'SERVER' else self.client
            if target:
                target.send(pickle.dumps(data))
        except Exception as e:
            print(f"Gönderme hatası: {e}")

    def get_data(self):
        data = self.received_data
        self.received_data = None
        return data