#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import random

class AkilliHaritala(Node):
    def __init__(self):
        super().__init__('akilli_haritala')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(LaserScan, 'scan', self.scan_callback, 10)
        self.twist = Twist()
        
        # Durumlar: 'ileri', 'geri', 'donuyor'
        self.state = 'ileri' 
        self.donus_yonu = 1 # 1: Sol, -1: Sağ
        self.sikiisma_sayaci = 0
        
        self.get_logger().info('Akıllı Haritalama Başlatıldı! (Geri Vites Özellikli)')

    def scan_callback(self, msg):
        ranges = msg.ranges
        num_readings = len(ranges)
        
        # --- 1. LİDAR VERİLERİNİ BÖLGELERE AYIR ---
        # Ön, Sol ve Sağ bölgelerdeki en yakın mesafeleri bul
        # (Lidar 360 derece olduğu için array'in başı ve sonu ön tarafı temsil eder)
        
        # Ön Taraf (Merkezdeki 60 derecelik açı)
        on_sol = ranges[0:30]
        on_sag = ranges[-30:]
        on_bolge = on_sol + on_sag
        min_on = min([x for x in on_bolge if x > 0.05], default=10.0)
        
        # Sol Taraf (30 ile 90 derece arası)
        sol_bolge = ranges[30:90]
        min_sol = min([x for x in sol_bolge if x > 0.05], default=10.0)
        
        # Sağ Taraf (-90 ile -30 derece arası)
        sag_bolge = ranges[-90:-30]
        min_sag = min([x for x in sag_bolge if x > 0.05], default=10.0)

        # --- 2. HAREKET MANTIĞI ---
        
        # DURUM 1: ACİL DURUM (Çok Yakın) - SIKIŞMA KURTARMA
        if min_on < 0.50: 
            self.get_logger().info(f'Çok yakın! Geri kaçılıyor... ({min_on:.2f}m)')
            self.state = 'geri'
            self.twist.linear.x = -0.15 # Geri git
            self.twist.angular.z = 0.0
            self.sikiisma_sayaci += 1
            
        # DURUM 2: ENGEL VAR (Dönme Zamanı)
        elif min_on < 1.0:
            self.state = 'donuyor'
            self.twist.linear.x = 0.0
            
            # Hangi taraf daha boşsa oraya dön
            if min_sol > min_sag:
                self.donus_yonu = 1 # Sola dön
            else:
                self.donus_yonu = -1 # Sağa dön
                
            # Eğer sıkışma sayacı arttıysa daha sert dön
            hiz_carpani = 1.0 + (self.sikiisma_sayaci * 0.1)
            self.twist.angular.z = 0.3 * self.donus_yonu * hiz_carpani

        # DURUM 3: YOL AÇIK (İlerle)
        else:
            self.state = 'ileri'
            self.sikiisma_sayaci = 0 # Sıkışma sıfırlandı
            self.twist.linear.x = 0.15 # Yavaş ve güvenli hız
            self.twist.angular.z = 0.0

        # Mesajı yayınla
        self.publisher_.publish(self.twist)

def main(args=None):
    rclpy.init(args=args)
    node = AkilliHaritala()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()