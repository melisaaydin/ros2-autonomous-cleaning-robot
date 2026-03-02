#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor #Aynı anda birden fazla işlemi çalıştırmak için
from std_msgs.msg import String #/app_komut topic’inden gelen mesaj tipi
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped #robotun hedef konumu için mesaj tipi
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult #basic nav. nav2 sistemini kolay kullanmak için hazır sınıf.Bu, ROS2 Navigation2 sistemine bağlanır
import threading
import time

class AppKontrol(Node):
    def __init__(self):
        super().__init__('app_kontrol_node')
        
        # 1. Komutları Dinle -string tipinde mesaj al. mesaj gelince komut_callback fonk. çalıştır
        self.subscription = self.create_subscription(
            String,
            '/app_komut',
            self.komut_callback,
            10)
        
        # 2. Başlangıç Konumunu Yayınla - AMCL sistemine robotun başlangıç konumu bildiriyor. Navigation başlamadan önce harita üzerindeki yeri söylenir
        self.initial_pose_pub = self.create_publisher(
            PoseWithCovarianceStamped,
            '/initialpose',
            10)

        self.navigator = BasicNavigator() #goToPose() gibi fonksiyonları kullanmamızı sağlar
        self.get_logger().info('✅ ROBOT KONTROL SİSTEMİ BAŞLATILDI...')

        # Hedef Listesi
        self.konumlar = {
            "salon":  {"x": -3.0, "y": -1.0, "w": 1.0},
            "mutfak": {"x": 3.0,  "y": 1.5,  "w": 0.7},
            "yatak":  {"x": 3.5,  "y": -2.0, "w": 0.0},
            "giris":  {"x": 0.0,  "y": 0.0,  "w": 1.0}
        }

        # Konumlandırma işlemini başlat
        #navigation sistemi açılmadan robot çalışmaz. bu yüzden AMCL hazır mı kontrol ediliyor, initialpose gönderiliyor,nav2 aktif olana kadar bekleniyor
        threading.Thread(target=self.otomatik_baslat).start()

    def otomatik_baslat(self):
        """AMCL hazır olana kadar bekle ve konumu ayarla"""
        self.get_logger().info('⏳ AMCL bekleniyor...')
        
        # AMCL dinleyene kadar bekle
        while self.initial_pose_pub.get_subscription_count() == 0: #/initialpose topic’ini dinleyen var mı? yoksa bekle
            time.sleep(0.5)
            if not rclpy.ok(): return

        self.get_logger().info('📡 AMCL Hazır! Konum gönderiliyor...')
        
        init_pose = PoseWithCovarianceStamped()
        init_pose.header.frame_id = 'map'
        init_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        init_pose.pose.pose.position.x = 0.0
        init_pose.pose.pose.position.y = 0.0
        init_pose.pose.pose.orientation.w = 1.0
        
        # Sinyali birkaç kez gönder -AMCL bazen ilk mesajı kaçırabiliyor.
        for _ in range(5):
            self.initial_pose_pub.publish(init_pose)
            time.sleep(0.2)
            
        self.get_logger().info('✅ Konum Ayarlandı! Navigasyon aktifleşiyor...')
        
        # Navigasyonun açılmasını bekle
        self.navigator.waitUntilNav2Active()
        self.get_logger().info('🚀 SİSTEM HAZIR! Komut verebilirsin.')

    def komut_callback(self, msg): #mesaj gelince çalışır
        komut = msg.data
        self.get_logger().info(f'📩 Sinyal Alındı: "{komut}"')

        # İşlemleri yeni thread'de başlat ki dinlemeyi kilitlemesin
        if komut == "devriye":
            threading.Thread(target=self.devriye_baslat).start()
        elif komut in self.konumlar:
            threading.Thread(target=self.tek_git, args=(komut,)).start()
        elif komut == "dur":
            self.navigator.cancelTask()
            self.get_logger().info('🛑 DURDURULDU!')

    #robot tek hedefe gider
    def tek_git(self, yer_adi):
        coords = self.konumlar[yer_adi]
        goal = PoseStamped()
        goal.header.frame_id = 'map'
        goal.header.stamp = self.navigator.get_clock().now().to_msg()
        goal.pose.position.x = coords["x"]
        goal.pose.position.y = coords["y"]
        goal.pose.orientation.w = coords["w"]
        
        self.get_logger().info(f'🚀 {yer_adi} hedefine gidiliyor...')
        self.navigator.goToPose(goal) #robot o konuma gitmeye başlar

    def devriye_baslat(self):
        rotalar = ["salon", "mutfak", "yatak", "giris"]
        for yer in rotalar:
            self.get_logger().info(f'>>> Gidiliyor: {yer}')
            coords = self.konumlar[yer]
            goal = PoseStamped() #hedef oluşturuluyor
            goal.header.frame_id = 'map'
            goal.header.stamp = self.navigator.get_clock().now().to_msg()
            goal.pose.position.x = coords["x"]
            goal.pose.position.y = coords["y"]
            goal.pose.orientation.w = coords["w"]
            
            self.navigator.goToPose(goal)
            
            while not self.navigator.isTaskComplete():
                time.sleep(1)
            
            time.sleep(2.0)

def main(args=None):
    rclpy.init(args=args)
    
    # Node'u oluştur
    node = AppKontrol()
    
    # MultiThreadedExecutor kullanarak çakışmaları önle
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    
    # Executor'ı ayrı bir thread'de döndürüyoruz
    # Bu sayede main thread boş kalır ve kilitlenme (deadlock) olmaz.
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()
    
    # Main thread sadece programın kapanmamasını sağlar
    try:
        while rclpy.ok():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
        
    rclpy.shutdown()
    spin_thread.join()

if __name__ == '__main__':
    main()


#AMCL = Robotun harita üzerindeki yerini tahmin eden sistemdir.Robot:Haritayı bilir ,Lidar’dan veri alır “Ben şu an haritanın neresindeyim?” sorusuna cevap bulur