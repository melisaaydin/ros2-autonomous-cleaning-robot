#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np #numpy → Lidar verilerini kolayca hesaplamak için.

class SupurgeBeyni(Node):
    def __init__(self):
        super().__init__('supurge_beyni')
        
        # Hız komutlarını yayınlayacak publisher
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10) #robotun hızını cmd_vel e gönderecek
        # Lidar verisini dinleyecek subscriber
        self.subscription = self.create_subscription(LaserScan, 'scan', self.scan_callback, 10) #her veri geldiğinde scan_callback fonksiyonu çağrılır. 10 → QoS derinliği (mesaj kuyruğu boyutu).
        self.get_logger().info('Süpürge beyni devrede! Temizlik başlıyor...')

    def scan_callback(self, msg):
        # Lidar verisini numpy dizisine çevir
        ranges = np.array(msg.ranges)
        
        # 'inf' (sonsuz) değerlerini 10 metre gibi güvenli bir sayıya çek
        ranges = np.nan_to_num(ranges, posinf=10.0, neginf=10.0)
        
        # Dizi uzunluğunu dinamik olarak bul
        uzunluk = len(ranges)
        orta_nokta = uzunluk // 2
        
        # Ön taraftaki tarama genişliği (Toplam açının %10'u kadar bir dilim)
        # Örneğin 360 veri varsa ortadaki 36 veriye bakar
        tarama_genisligi = int(uzunluk * 0.1) 
        
        # Tam önümüzdeki dilimi alıyoruz
        baslangic = orta_nokta - (tarama_genisligi // 2)
        bitis = orta_nokta + (tarama_genisligi // 2)
        
        on_bolge = ranges[baslangic:bitis]
        
        if len(on_bolge) > 0:
            minimum_on_mesafe = np.min(on_bolge)
        else:
            minimum_on_mesafe = 10.0 # Veri yoksa güvenli say

        twist = Twist()

        # MESAFE MANTIĞI:
        # Eğer önünde 70 cm'den yakın engel varsa -> Dön
        # Yoksa -> İlerle
        
        if minimum_on_mesafe < 0.7:  
            self.get_logger().info(f'ENGEL VAR! Mesafe: {minimum_on_mesafe:.2f}m. Sağa dönülüyor...')
            twist.linear.x = 0.0
            twist.angular.z = -0.5  # Eksi değer sağa döndürür (genelde)
        else:
            # self.get_logger().info(f'Yol temiz. İlerleniyor... ({minimum_on_mesafe:.2f}m)')
            twist.linear.x = 0.2  # İleri hız
            twist.angular.z = 0.0

        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = SupurgeBeyni()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()