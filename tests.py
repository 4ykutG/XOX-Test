import time
from tabulate import tabulate

# --- 1. TEST EDİLECEK MODLAR ---
oyun_modlari = ["Bilgisayara Karşı (PvE)", "Aynı Bilgisayardan 2 Kişilik", "LAN Modu"]

# --- 2. TEST SENARYOLARI (Gönderdiğin Resimdeki Formata Uygun) ---
test_senaryolari = [
    {
        "id": "TC-01",
        "konu": "Bağlantı Kopması / Oyundan Çıkma",
        "risk": "Yüksek",
        "girdi": "Oyun sırasında oyuncunun çıkış yapması veya bağlantının kesilmesi",
        "beklenen": "Oyun durmalı, kalan oyuncu 'Hükmen Galip' sayılmalı",
    },
    {
        "id": "TC-02",
        "konu": "10 Saniye Süre Aşımı",
        "risk": "Orta",
        "girdi": "Sırası gelen oyuncunun 10 saniye hamle yapmaması",
        "beklenen": "Süre dolduğunda sıra otomatik olarak diğer oyuncuya geçmeli",
    },
    {
        "id": "TC-03",
        "konu": "Kazanma Koşulu",
        "risk": "Yüksek",
        "girdi": "Oyuncunun gerekli puanı/kareyi tamamlaması",
        "beklenen": "Kazanan tebrik ekranı açılmalı ve skor kaydedilmeli",
    }
]

sonuclar = []

print("--- YAZILIM TEST SENARYOLARI KOŞULUYOR ---\n")

# --- 3. TEST DÖNGÜSÜ ---
for mod in oyun_modlari:
    
    # KURAL: LAN Modu ise bu testleri yapma (Daha önce konuştuğumuz gibi)
    if "LAN" in mod:
        # İsteğe bağlı: Raporda görünmesi için 'SKIPPED' ekleyebilirsin
        continue 

    print(f"[{mod}] modu için senaryolar test ediliyor...")

    for test in test_senaryolari:
        
        # Test Simülasyonu (Burada gerçek test fonksiyonları çağrılır)
        # Örn: result = run_test(mod, test['id'])
        time.sleep(0.5) # İşlem simülasyonu
        
        # Senaryoya göre gerçekleşen sonuçları simüle edelim
        if test["id"] == "TC-01":
            gerceklesen = "Oyun bitti, rakip galip ilan edildi."
            durum = "PASS"
        elif test["id"] == "TC-02":
            gerceklesen = "Süre bitti, sıra karşı tarafa geçti."
            durum = "PASS"
        elif test["id"] == "TC-03":
            gerceklesen = "Win ekranı açıldı, puan eklendi."
            durum = "PASS"
            
        # Sonuçları Tablo Verisine Ekle
        sonuclar.append([
            mod,
            test["konu"],
            test["risk"],
            test["girdi"],
            test["beklenen"],
            gerceklesen, # Actual Output
            durum
        ])

# --- 4. RAPORLAMA (TABLO ÇIKTISI) ---
print("\n" + "="*120)
print("TEST SONUÇ RAPORU")
print("="*120)

headers = ["Mod", "Senaryo", "Risk", "Girdi (Input)", "Beklenen Çıktı", "Gerçekleşen", "DURUM"]

# Tabloyu ekrana bas (Tablefmt 'grid' veya 'fancy_grid' kullanılabilir)
print(tabulate(sonuclar, headers=headers, tablefmt="grid"))