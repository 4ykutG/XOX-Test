# gui_client.py (Nihai Sürüm: Skor, Yenileme Butonu ve Geliştirilmiş Görünüm)
import tkinter as tk
from tkinter import messagebox
import socket
import threading
from utils import serialize_data, deserialize_data, HOST, PORT
import time 

class XOXClient:
    def __init__(self, master):
        self.master = master
        master.title("Ağ Üzerinden XOX")
        master.configure(bg='#34495e') # Arka plan rengi (Koyu gri/Mavi)
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Ağ ve Oyun Durumu Değişkenleri
        self.client_socket = None
        self.is_connected = False
        self.player_symbol = ''
        self.board = [' '] * 9
        self.turn = ''
        self.status = ''
        self.scores = {'X': 0, 'O': 0}
        self.game_active = False

        # --- GUI BİLEŞENLERİ ---
        
        # SKOR ÇUBUĞU EKLENDİ (Üstte)
        self.score_frame = tk.Frame(master, bg='#2c3e50')
        self.score_frame.pack(fill='x', padx=10, pady=5)
        
        self.score_label_x = tk.Label(self.score_frame, text="X Skoru: 0", fg='#3498db', bg='#2c3e50', font=('Arial', 14, 'bold'))
        self.score_label_x.pack(side='left', padx=20, pady=5)
        
        self.score_label_o = tk.Label(self.score_frame, text="O Skoru: 0", fg='#e74c3c', bg='#2c3e50', font=('Arial', 14, 'bold'))
        self.score_label_o.pack(side='right', padx=20, pady=5)
        
        # Durum Çubuğu
        self.status_label = tk.Label(master, text="Bağlanılıyor...", bd=1, relief="sunken", anchor="w", 
                                     font=('Arial', 12, 'bold'), bg='#ecf0f1')
        self.status_label.pack(fill='x', padx=10, pady=5)
        
        # Tahta Çerçevesi
        self.board_frame = tk.Frame(master, bg='#34495e')
        self.board_frame.pack(padx=10, pady=10)
        
        self.buttons = []
        for i in range(9):
            row = i // 3
            col = i % 3
            btn = tk.Button(self.board_frame, text="", font=('Consolas', 36, 'bold'), width=3, height=1,
                            bg='#ecf0f1', activebackground='#bdc3c7', fg='black',
                            command=lambda i=i: self.make_move(i))
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            self.buttons.append(btn)
            
        # Kontrol Butonları (Altta)
        self.control_frame = tk.Frame(master, bg='#34495e')
        self.control_frame.pack(pady=10)
        
        self.connect_button = tk.Button(self.control_frame, text="Sunucuya Bağlan", command=self.connect_to_server, font=('Arial', 10, 'bold'), bg='#2ecc71', fg='white')
        self.connect_button.pack(side='left', padx=10)
        
        # YENİLEME BUTONU EKLENDİ
        self.restart_button = tk.Button(self.control_frame, text="Yeni Tur", command=self.request_restart, state='disabled', font=('Arial', 10, 'bold'), bg='#f39c12', fg='white')
        self.restart_button.pack(side='left', padx=10)
        
        self.update_gui()

    def update_gui(self):
        """Oyun tahtasını ve durumu günceller. Skorları ve buton durumunu yönetir."""
        
        # 1. Tahta ve Renkleri Güncelle
        for i in range(9):
            self.buttons[i]['text'] = self.board[i]
            
            if self.board[i] == 'X':
                self.buttons[i]['fg'] = '#3498db'
            elif self.board[i] == 'O':
                self.buttons[i]['fg'] = '#e74c3c'
            else:
                self.buttons[i]['fg'] = 'black'
            
            # Buton durumları
            if self.game_active and self.turn == self.player_symbol and self.board[i] == ' ':
                self.buttons[i]['state'] = 'normal'
            else:
                self.buttons[i]['state'] = 'disabled'

        # 2. Skorları Güncelle (Skor Etiketleri Eklendi)
        self.score_label_x['text'] = f"X Skoru: {self.scores.get('X', 0)}"
        self.score_label_o['text'] = f"O Skoru: {self.scores.get('O', 0)}"

        # 3. Durum Çubuğu ve Butonları Güncelle
        if not self.is_connected:
            self.status_label['text'] = "Bağlantı Kesik. Lütfen Bağlanın."
            self.status_label['bg'] = '#e74c3c'
        elif self.status == 'WAITING':
             self.status_label['text'] = f"Sembolün: {self.player_symbol}. Rakip bekleniyor..."
             self.status_label['bg'] = '#f1c40f'
             self.restart_button['state'] = 'disabled'
        elif self.status == 'PLAYING':
            if self.turn == self.player_symbol:
                self.status_label['text'] = f"SIRA SENDE! ({self.player_symbol})"
                self.status_label['bg'] = '#2ecc71'
            else:
                self.status_label['text'] = f"Rakip ({self.turn}) bekleniyor..."
                self.status_label['bg'] = '#f1c40f'
            self.restart_button['state'] = 'disabled'
        elif self.status.startswith('WINNER'):
            winner = self.status.split(': ')[1]
            self.status_label['text'] = f"OYUN BİTTİ! KAZANAN: {winner}"
            self.status_label['bg'] = '#d35400'
            self.game_active = False
            self.restart_button['state'] = 'normal' # Yenileme butonu aktif
        elif self.status == 'DRAW':
            self.status_label['text'] = "OYUN BİTTİ! BERABERLİK."
            self.status_label['bg'] = '#95a5a6'
            self.game_active = False
            self.restart_button['state'] = 'normal' # Yenileme butonu aktif
        elif self.status == 'DISCONNECTED':
            self.status_label['text'] = "RAKİP BAĞLANTISI KESİLDİ. OYUN BİTTİ."
            self.status_label['bg'] = '#e74c3c'

    def connect_to_server(self):
        """Sunucuya bağlanmaya çalışır."""
        if self.is_connected:
            messagebox.showinfo("Bilgi", "Zaten bağlısınız.")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            self.is_connected = True
            self.connect_button['text'] = "Bağlandı"
            self.connect_button['state'] = 'disabled'
            
            threading.Thread(target=self.listen_for_updates, daemon=True).start()
            self.status_label['text'] = "Bağlantı başarılı, rakip bekleniyor..."
            
        except ConnectionRefusedError:
            messagebox.showerror("Hata", "Sunucuya bağlanılamadı. Sunucu çalışıyor mu?")
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmedik bir hata oluştu: {e}")

    def listen_for_updates(self):
        """Sunucudan gelen verileri sürekli dinler."""
        try:
            # İlk veri bloku
            initial_data = self.client_socket.recv(4096)
            if not initial_data:
                 raise ConnectionResetError("Sunucudan başlangıç verisi alınamadı.")
                 
            initial_state = deserialize_data(initial_data)
            
            self.player_symbol = initial_state.get('symbol', '')
            self.scores = initial_state.get('scores', {'X': 0, 'O': 0})
            self.board = initial_state.get('board', [' '] * 9)
            self.turn = initial_state.get('turn', 'X')
            self.status = initial_state.get('status', 'WAITING')
            
            if self.status in ['PLAYING', 'WAITING']:
                self.game_active = True
            
            self.master.after(0, self.update_gui)
            
            # Oyun döngüsü
            while self.is_connected:
                data = self.client_socket.recv(4096)
                
                if not data:
                    self.status = 'DISCONNECTED'
                    break
                    
                game_state = deserialize_data(data)
                
                self.board = game_state.get('board', self.board)
                self.turn = game_state.get('turn', self.turn)
                self.status = game_state.get('status', self.status)
                self.scores = game_state.get('scores', self.scores) # Skor güncelleniyor!

                if self.status not in ['PLAYING', 'WAITING']:
                    self.game_active = False
                    
                self.master.after(0, self.update_gui)
                
        except socket.error as e:
            print(f"[AĞ HATASI] Bağlantı kesildi: {e}")
            self.status = 'DISCONNECTED'
            self.master.after(0, self.update_gui)
        except Exception as e:
            print(f"[GENEL HATA] Dinleme hatası: {e}")
            self.status = 'DISCONNECTED'
            self.master.after(0, self.update_gui)
        finally:
            self.is_connected = False
            if self.client_socket:
                self.client_socket.close()
            self.master.after(0, self.update_gui)
            
    def make_move(self, index):
        """GUI'de bir butona tıklandığında hamleyi sunucuya gönderir."""
        if self.is_connected and self.game_active and self.turn == self.player_symbol:
            if self.board[index] == ' ':
                try:
                    self.client_socket.send(serialize_data(index))
                    self.turn = 'WAITING_FOR_SERVER' 
                    self.update_gui()
                except socket.error:
                    messagebox.showerror("Hata", "Hamle gönderilemedi, bağlantı kesilmiş olabilir.")
            else:
                messagebox.showwarning("Uyarı", "Bu alan dolu!")
                
    def request_restart(self):
        """Sunucuya yeni tur başlatma isteği gönderir."""
        if self.is_connected and (self.status.startswith('WINNER') or self.status == 'DRAW'):
            try:
                # RESTART komutunu sunucuya gönder
                self.client_socket.send(serialize_data("RESTART"))
                self.restart_button['state'] = 'disabled' 
                self.status_label['text'] = "Yenileme isteği gönderildi. Rakip bekleniyor..."
                self.status_label['bg'] = '#f1c40f'
                
            except socket.error:
                messagebox.showerror("Hata", "Yenileme isteği gönderilemedi, bağlantı kesilmiş olabilir.")

    def on_closing(self):
        """Pencere kapatıldığında soketi kapatır."""
        if self.is_connected:
            try:
                self.client_socket.close()
            except:
                pass
        self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = XOXClient(root)
    root.mainloop()