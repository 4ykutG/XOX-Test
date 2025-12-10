# ❌⭕ XOX Oyunu ve Test Dokümantasyonu

**Ders:** YZM 3111 - Yazılım Testi  
**Proje:** XOX (Tic-Tac-Toe) Oyunu Test Otomasyonu ve Raporlama

Bu proje, YZM 3111 dersi kapsamında geliştirilmiş; **Birim (Unit)** ve **Entegrasyon** test süreçleri uygulanarak güvenilirliği doğrulanmış bir XOX oyunudur.

---

## 📸 Proje ve Test Görselleri

Projenin çalışma anına ve test süreçlerine ait görseller aşağıdadır.

### 1. Test Senaryosu Tasarımı (Test Case Design)
Oyun alanının oluşturulması ve oyun akışının doğrulanması için hazırlanan test senaryosu örneği:

![Test Case Tablosu](./testcase.jpg)
*(Yukarıdaki görsel, projenin Risk Seviyesi, Girdiler ve Beklenen Çıktılarını içeren orijinal test dokümanıdır.)*

### 2. Test Koşum Sonucu (Terminal Çıktısı)
Yazılan test otomasyon kodunun (Python) çalıştırılması sonucu elde edilen "PASS" (Başarılı) tablosu:

![Test Terminal Çıktısı](./assets/terminal_output.png)
---

## 🧪 Yazılım Test Süreçleri ve Kalite Güvencesi (QA)

Test sürecinde **LAN Modu** kapsam dışı bırakılmış, odak noktası **PvE (Yapay Zeka)** ve **Local PvP** modlarının kararlılığı üzerine yoğunlaşmıştır.

### ✅ Özet Test Sonuç Tablosu

Aşağıdaki tablo, proje kapsamında gerçekleştirilen test senaryolarının (Test Cases) özet sonuçlarını içermektedir.

| Test ID | Mod | Senaryo | Risk | Beklenen Sonuç | Gerçekleşen Sonuç | Durum |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | PvE | Bağlantı Kopması | Yüksek | Oyun durmalı, çıkış güvenli yapılmalı. | Oyun durduruldu, menüye dönüldü. | **PASS** |
| **TC-02** | PvE | 10sn Süre Aşımı | Orta | Sıra otomatik olarak AI'ya geçmeli. | Sayaç sıfırlandı, sıra AI'ya geçti. | **PASS** |
| **TC-03** | PvE | Kazanma Koşulu | Yüksek | Skor güncellenmeli, Win ekranı açılmalı. | Puan eklendi, tebrik ekranı geldi. | **PASS** |
| **TC-04** | PvP | Bağlantı Kopması | Yüksek | Kalan oyuncu hükmen galip sayılmalı. | Kalan oyuncu galip ilan edildi. | **PASS** |
| **TC-05** | PvP | 10sn Süre Aşımı | Orta | Sıra rakip oyuncuya devredilmeli. | Süre doldu, hak devredildi. | **PASS** |
| **TC-06** | PvP | Kazanma Koşulu | Yüksek | Galibiyet ekranı doğru oyuncuya çıkmalı. | Doğru oyuncu için Win ekranı açıldı. | **PASS** |

---

## 🛠️ Detaylı Test Senaryoları (Test Cases)

### 1. Bağlantı Kopması ve İstisna Yönetimi
* **Amaç:** Oyun esnasında kullanıcının pencereyi kapatması durumunda oyunun çökmemesini sağlamak.
* **Risk:** Yüksek
* **Sonuç:** Sistem hatayı yakaladı ve ana menüye yönlendirme yaptı.

### 2. 10 Saniye Kuralı (Zaman Aşımı Testi)
* **Amaç:** Oyun akışının sürekliliğini sağlamak.
* **Girdi:** Kullanıcı 10 saniye boyunca hamle yapmaz.
* **Sonuç:** Zamanlayıcı 0'a ulaştığında sıra otomatik olarak karşı tarafa geçti.

### 3. Kazanma ve Skor Doğrulama
* **Amaç:** Oyunun mantıksal sonucunun doğruluğunu test etmek.
* **Beklenen:** Yatay, dikey veya çapraz eşleşmede oyun bitmeli.
* **Sonuç:** Algoritma kazananı doğru tespit etti.

---

## 🚀 Kurulum ve Test Çalıştırma

Testleri kendi makinenizde simüle etmek için:

```bash
# Gerekli kütüphaneyi kurun
pip install tabulate
pip install pygame

# Test senaryolarını çalıştırın
python tests.py.py