#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import time

class DuvarTakip(Node):
    def __init__(self):
        super().__init__('duvar_takip')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(LaserScan, 'scan', self.scan_callback, 10)
        self.twist = Twist()
        self.state = "duvar_ara" # Durumlar: duvar_ara, takip_et, sola_don, kurtar
        self.get_logger().info('Duvar Takip Modu Başlatıldı! Sağ tarafı takip ediyorum...')

    def scan_callback(self, msg):
        # Lidar verilerini 4 bölgeye ayır
        ranges = msg.ranges
        n = len(ranges)
        
        # Lidar indexleri 
        # Ön: 0, Sağ: 270 (-90), Sol: 90, Arka: 180
        # Simülasyon verisine göre dilimleme:
        
        # Ön Taraf (Merkezdeki 20 derece)
        on_dilim = ranges[0:15] + ranges[-15:]
        on_mesafe = min([x for x in on_dilim if x > 0.05], default=10.0)
        
        # Sağ Taraf (Saat 3 ile 5 yönü arası)
        sag_dilim = ranges[-100:-40] 
        sag_mesafe = min([x for x in sag_dilim if x > 0.05], default=10.0)
        
        # Sağ Ön Çapraz (Çarpmayı önlemek için kritik)
        sag_on_dilim = ranges[-40:-15]
        sag_on_mesafe = min([x for x in sag_on_dilim if x > 0.05], default=10.0)

        # --- MANTIK (State Machine) ---
        
        # 1. ACİL DURUM: Çok yaklaştıysan (Sıkışma Önleyici)
        if on_mesafe < 0.25 or sag_on_mesafe < 0.20:
            self.state = "kurtar"
            self.twist.linear.x = -0.2 # Geri git
            self.twist.angular.z = 0.5 # Geri giderken burnunu çevir
            self.get_logger().warning('Çok yakın! Geri kaçılıyor...')

        # 2. ÖNÜ KAPALI: Duvar veya köşe geldi -> Sola Dön
        elif on_mesafe < 0.6:
            self.state = "sola_don"
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.4 # Olduğu yerde sola dön

        # 3. DUVAR TAKİBİ
        else:
            self.state = "takip_et"
            self.twist.linear.x = 0.2 # İleri git
            
            # Duvarı kaybetme veya çok yaklaşma ayarı
            # Hedef: Duvardan 50cm uzakta kalmak
            
            if sag_mesafe > 0.7: 
                # Duvar uzaklaştı, sağa yanaş (Duvarı bul)
                self.twist.angular.z = -0.25 
            elif sag_mesafe < 0.4:
                # Duvar çok yakın, sola kaç
                self.twist.angular.z = 0.25
            else:
                # Mesafe mükemmel, düz git
                self.twist.angular.z = 0.0

        self.publisher_.publish(self.twist)

def main(args=None):
    rclpy.init(args=args)
    node = DuvarTakip()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()