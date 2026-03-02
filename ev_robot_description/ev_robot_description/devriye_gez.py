#!/usr/bin/env python3
import time
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy
from math import pi

def main():
    rclpy.init()
    navigator = BasicNavigator()

    # Navigasyonun hazır olmasını bekle
    print("Navigasyon sistemi bekleniyor...")
    navigator.waitUntilNav2Active()
    print("Navigasyon AKTİF! Devriye başlıyor.")

    # --- SDF DOSYASINA GÖRE HESAPLANAN HEDEFLER ---
    hedefler = [
        # 1. SALON (Koltuk ve sehpanın arası)
        {"isim": "Salon",       "x": -3.0, "y": -1.0, "w": 1.0},
        
        # 2. MUTFAK (Yemek masasının yanı)
        {"isim": "Mutfak",      "x": 3.0,  "y": 1.5,  "w": 0.7},
        
        # 3. YATAK ODASI (Dolabın önü)
        {"isim": "Yatak Odasi", "x": 3.5,  "y": -2.0, "w": 0.0},
        
        # 4. BAŞLANGIÇ (Koridor/Merkez)
        {"isim": "Giris",       "x": 0.0,  "y": 0.0,  "w": 1.0}
    ]

    for yer in hedefler:
        print(f"\n>>> {yer['isim']} konumuna gidiliyor... (x={yer['x']}, y={yer['y']})")
        
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = navigator.get_clock().now().to_msg()
        
        goal_pose.pose.position.x = yer["x"]
        goal_pose.pose.position.y = yer["y"]
        # Dönüş açısı (Odaya girince nereye baksın)
        goal_pose.pose.orientation.z = 0.0 
        goal_pose.pose.orientation.w = yer["w"]

        navigator.goToPose(goal_pose)

        i = 0
        while not navigator.isTaskComplete():
            # Her 2 saniyede bir geri bildirim ver
            i += 1
            if i % 20 == 0:
                feedback = navigator.getFeedback()
                if feedback:
                    print(f"   Mesafe: {feedback.distance_remaining:.2f}m kaldı.")
            time.sleep(0.1)

        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print(f"*** {yer['isim']} hedefine ulaşıldı! ***")
            print("   (Etraf kontrol ediliyor - 3 saniye bekleme)")
            time.sleep(3.0) 
        else:
            print(f"!!! {yer['isim']} hedefine gidilemedi! İptal edildi. !!!")

    print("\n--------------------------------")
    print("TÜM GÖREVLER TAMAMLANDI! Robot üsse döndü.")
    navigator.lifecycleShutdown()
    exit(0)

if __name__ == '__main__':
    main()