# utils.py
import pickle

# Not: Sunucu ve istemci için aynı HOST ve PORT kullanılmalıdır.
# HOST, genellikle Sunucunun IP adresi olacaktır.
# Burada varsayılan değerleri tanımlıyoruz.
HOST = '127.0.0.1' # Test için localhost, farklı cihazlar için sunucunun LAN IP'si olmalı (örn: '192.168.1.5')
PORT = 65432       # 1024 üzeri herhangi bir port olabilir.

def serialize_data(data):
    """Python verisini (liste, dict) pickle kullanarak ağ üzerinden gönderilebilecek
    ikili (binary) formata dönüştürür."""
    return pickle.dumps(data)

def deserialize_data(binary_data):
    """İkili (binary) veriyi tekrar Python nesnesine dönüştürür."""
    return pickle.loads(binary_data)