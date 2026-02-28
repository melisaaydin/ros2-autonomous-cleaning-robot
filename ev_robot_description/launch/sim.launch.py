import os #dosya yollarını oluşturmak
from ament_index_python.packages import get_package_share_directory #belirli bir ros2 paketinin share klasörünün yolunu alır. 
from launch import LaunchDescription #launch dosyasında hangi nodeların başlatılacağını belirlemek
from launch.actions import IncludeLaunchDescription #başka bir launch dosyası çağırmak için
from launch.launch_description_sources import PythonLaunchDescriptionSource #başlatılacak launch dosyasını python dosyası oldugunu belirtir
from launch_ros.actions import Node #node başlatmak için
import xacro #urdf robot tanımlarını işlemek için

def generate_launch_description():
    robot_name = 'ev_hizmet_robotu'
    pkg_path = get_package_share_directory('ev_robot_description')
    world_file = os.path.join(pkg_path, 'worlds', 'ev_ortami.sdf')
    # Xacro işle
    xacro_file = os.path.join(pkg_path, 'urdf', 'robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    # Gazebo Sim - Standart Apartman Dünyası
    # IncludeLaunchDescription → Başka bir launch dosyasını çağırır (gz_sim.launch.py Gazebo simülasyonu için).
    #launch_arguments → -r {world_file} → Belirtilen dünya (.sdf) dosyasını yükle ve başlat.
    #ros_gz_sim → Gazebo (Ignition Gazebo) ROS2 paketi.
    gazebo = IncludeLaunchDescription( 
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )

    # Robot State Publisher
    # robot_state_publisher → URDF’deki tüm eklem (joint) pozisyonlarını TF çerçevelerine dönüştürür ve yayınlar.
    # robot_description → Robot URDF XML’i.
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    # Spawn Robot - robotu gazeboya spawn(yerleştirme) eder. z 0.1 robotun z ekseninde başlangıç yüksekliği
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', robot_name, '-z', '0.1']
    )

    # Bridge
    #Odometri robotun base_link çerçevesini hesaplar → /odom çerçevesi.
    #Lidar sensörü laser çerçevesindedir → TF ile base_link’e göre konumu bilinir.
    #Robot harita üzerinde hareket ederken, TF sayesinde tüm sensör verileri aynı koordinat sisteminde birleştirilir.
    bridge = Node(
        package='ros_gz_bridge', #ros2 gazebo arasında veri aktarımı(bridge)
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan', #lidar(ışık tespiti mezil ölçümü) taraması -- lidar,robotun etrafına lazer ışığı gönderir. ışığın geliş gidiş süresini ölçerek neseye olan uzaklığı hesaplar.lidar harita gibi görünüm elde eder
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist', # robot hız komutu
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry', #odometri bilgisi --robotun zaman içinde ne kadar hareket ettiğini ve hangi konumda olduğunu tahmin etme. bu genellikle tekerlek sensörlerinden(encoder) gelir.haritalama(SLAM) için giriş verisi.uzak mesafelerde pozisyon hatası artar bu yüzden genellikle IMU + Lidar/Camera ile düzeltilir
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V', #TF ros2'da robot parçaları arasındaki koordinat frames ilişkisini yönetmek için kullanılır.tf Robotun farklı parçalarının pozisyonunu birbirine göre bilmesini sağlar.
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        output='screen' #çıktıları terminalde göster
    )
   
    return LaunchDescription([
        rsp,
        gazebo,
        spawn,
        bridge
    ])