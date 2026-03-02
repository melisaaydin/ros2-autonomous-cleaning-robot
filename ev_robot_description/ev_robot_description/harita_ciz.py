#!/usr/bin/env python3
import numpy as np
import yaml
import os

def pgm_olustur():
    # --- HARİTA AYARLARI ---
    genislik_metre = 20.0
    yukseklik_metre = 20.0
    cozunurluk = 0.05
    
    w_px = int(genislik_metre / cozunurluk)
    h_px = int(yukseklik_metre / cozunurluk)
    
    # 254 = Beyaz (Boş), 0 = Siyah (Duvar)
    harita = np.full((h_px, w_px), 254, dtype=np.uint8)
    
    cx = w_px // 2
    cy = h_px // 2
    
    def metreden_piksele(x, y):
        c = int(x / cozunurluk) + cx
        r = cy - int(y / cozunurluk) 
        return c, r

    def kutu_ciz(x_merkez, y_merkez, w_m, h_m):
        c, r = metreden_piksele(x_merkez, y_merkez)
        w_p = int(w_m / cozunurluk)
        h_p = int(h_m / cozunurluk)
        r_start = max(0, r - h_p//2)
        r_end = min(h_px, r + h_p//2)
        c_start = max(0, c - w_p//2)
        c_end = min(w_px, c + w_p//2)
        harita[r_start:r_end, c_start:c_end] = 0

    # --- DUVARLARI ÇİZ (KAPILAR AÇIK!) ---
    
    # Dış Çerçeve (Aynı)
    kutu_ciz(0, 5, 12.2, 0.2)
    kutu_ciz(0, -5, 12.2, 0.2)
    kutu_ciz(-6, 0, 0.2, 10.2)
    kutu_ciz(6, 0, 0.2, 10.2)
    
    # --- İÇ DUVARLAR VE KAPILAR ---
    
    # 1. SALON DUVARI (Ortada boşluk bıraktık)
    # Eski: kutu_ciz(-1, 0, 0.2, 4.0) -> Kapalıydı
    # Yeni: Üst ve Alt parça, ortası boş
    kutu_ciz(-1, 2.5, 0.2, 2.0)  # Üst parça
    kutu_ciz(-1, -2.5, 0.2, 2.0) # Alt parça
    
    # 2. MUTFAK GİRİŞİ (Boşluklu)
    # Eski: kutu_ciz(3, 1.5, 3.0, 0.2)
    # Yeni: Sol tarafı kapalı, sağ tarafı açık
    kutu_ciz(1.5, 1.5, 1.0, 0.2) # Girişin solundaki duvar
    
    # 3. YATAK ODASI GİRİŞİ (Boşluklu)
    # Eski: kutu_ciz(3, -1.5, 3.0, 0.2)
    # Yeni: Sol tarafı kapalı, sağ tarafı açık
    kutu_ciz(1.5, -1.5, 1.0, 0.2) # Girişin solundaki duvar
    
    # Mobilyalar (Robot çarpmadan etrafından dolaşsın)
    kutu_ciz(-3.5, 2.5, 1.0, 1.0) # Sehpa
    kutu_ciz(3.5, 3.5, 1.5, 1.0)  # Masa
    kutu_ciz(-3.5, -3.0, 1.5, 1.5) # Koltuk
    kutu_ciz(4.0, -3.5, 1.0, 2.0)  # Dolap

    return harita, w_px, h_px, cx, cy

def kaydet():
    harita, w, h, cx, cy = pgm_olustur()
    
    # Dosyaları doğru klasöre kaydedelim
    klasor = os.path.expanduser("~/ros2_ws/src/ev_robot_description/maps/")
    pgm_dosya = os.path.join(klasor, "kusursuz_harita.pgm")
    yaml_dosya = os.path.join(klasor, "kusursuz_harita.yaml")

    with open(pgm_dosya, 'wb') as f:
        header = f"P5\n{w} {h}\n255\n".encode()
        f.write(header)
        f.write(harita.tobytes())
    
    # Origin hesaplama
    origin_x = - (w * 0.05) / 2.0
    origin_y = - (h * 0.05) / 2.0
    
    data = {
        'image': "kusursuz_harita.pgm", # Sadece dosya adı
        'resolution': 0.05,
        'origin': [origin_x, origin_y, 0.0],
        'negate': 0,
        'occupied_thresh': 0.65,
        'free_thresh': 0.196,
        'mode': 'trinary'
    }
    
    with open(yaml_dosya, 'w') as f:
        yaml.dump(data, f)
    
    print("Harita GÜNCELLENDİ: Kapılar artık açık!")

if __name__ == "__main__":
    kaydet()
