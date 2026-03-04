# 🤖 ROS 2 Autonomous Home Service Robot & Web Control Interface

![Web Interface](https://github.com/user-attachments/assets/7c3f6b9e-5261-4838-97c7-47bd94a9e36f)

## 📖 Proje Hakkında

Bu proje, ev ortamında görev yapan bir hizmet robotunun simülasyonunu, otonom navigasyonunu ve **Modern React Web Arayüzü** ile uzaktan kontrolünü içerir.

Robot, **ROS 2 Jazzy** üzerinde çalışmakta olup, **Nav2** ile otonom sürüş gerçekleştirmekte ve Lidar sensör verilerini kullanarak engellerden kaçınmaktadır. Geliştirilen **Full-Stack** yapı sayesinde, robot herhangi bir teknik bilgiye ihtiyaç duymadan bir web paneli üzerinden yönetilebilir.

## ✨ Özellikler

* **🗺️ SLAM & Haritalama:** Lidar sensörü kullanılarak evin 2D haritasının çıkarılması.
* **📍 Otonom Navigasyon (Nav2):** Belirlenen odalara (Salon, Mutfak, Yatak Odası) dinamik engel takibi ile otonom sürüş.
* **💻 React Web Kontrol Paneli:** `roslibjs` ve `rosbridge` kullanılarak geliştirilen, karanlık mod destekli modern arayüz.
* **🔄 Otomatik Başlatma:** AMCL (Konumlandırma) sistemi için otomatik `Initial Pose` ataması.
* **🚨 Devriye Modu:** Tek tuşla tüm evi sırasıyla gezen görev algoritması.
* **🛑 Acil Durdurma:** Web arayüzü üzerinden anlık müdahale sistemi.

## 🛠️ Kullanılan Teknolojiler

| Kategori | Teknolojiler |
| :--- | :--- |
| **Robotik** | ROS 2 (Jazzy), Gazebo Sim, Nav2, SLAM Toolbox |
| **Web** | React.js, HTML5/CSS3 (Dark UI), Node.js |
| **İletişim** | Rosbridge Server, Roslibjs |
| **Diller** | Python (Kontrol Node'u), C++ (Pluginler), JavaScript |

## 📸 Galeri

| Simülasyon Ortamı (Gazebo) | Navigasyon ve Harita (RViz) |
| :---: | :---: |
| ![Gazebo](https://github.com/user-attachments/assets/dc33f1a8-c77e-447d-91b0-1cdc114c1f46) | ![RViz](https://github.com/user-attachments/assets/a2fb9d3d-78c4-4978-9d69-1af336fe69a0) |
| *Ev Ortamı Simülasyonu* | *Maliyet Haritası ve Lidar Verisi* |

## 🚀 Kurulum

Bu projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin.

### 1. Ön Hazırlıklar
* Ubuntu 24.04
* ROS 2 Jazzy
* Node.js & npm

### 2. Projeyi Klonlayın
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone [https://github.com/melisaaydin/ros2-autonomous-cleaning-robot.git](https://github.com/melisaaydin/ros2-autonomous-cleaning-robot.git)

## **3. Bağımlılıkları Yükleyin**

### **ROS Bağımlılıkları**

Aşağıdaki komutları kullanarak gerekli ROS bağımlılıklarını yükleyin:

```bash
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup ros-jazzy-slam-toolbox ros-jazzy-rosbridge-server
```

### **Web Arayüzü Bağımlılıkları**

Web arayüzü bağımlılıklarını yüklemek için aşağıdaki adımları izleyin:

1. Klasör yolunuzu repo yapınıza göre düzenleyin:

```bash
cd ~/ros2_ws/src/ros2-autonomous-cleaning-robot/ev_robot_description/web_ui
```

2. Ardından, bağımlılıkları yüklemek için şu komutu çalıştırın:

```bash
npm install
```

## **4. Projeyi Derleyin**

Projeyi derlemek için aşağıdaki adımları takip edin:

1. Projeye ait ana dizine gidin:

```bash
cd ~/ros2_ws
```

2. Ardından, aşağıdaki komutla projeyi derleyin:

```bash
colcon build
```

3. Son olarak, derlenen projeyi çalıştırmak için ortamı yükleyin:

```bash
source install/setup.bash
```


## **🎮 Kullanım**

Proje, tek bir launch dosyası ile tüm simülasyon ve arka plan servislerini ayağa kaldırır. Web arayüzü ayrı bir terminalde çalıştırılır.

### **Adım 1: Robotu ve ROS Sistemini Başlatın**

İlk olarak, ROS ve robot sistemi için gerekli servisleri başlatmak için aşağıdaki komutu çalıştırın:

```bash id="xy6q2r"
# Terminal 1
export LIBGL_ALWAYS_SOFTWARE=1
ros2 launch ev_robot_description hepsini_baslat.launch.py
```

Bu komut, Gazebo simülasyon ortamını, Nav2 navigasyon sistemini, RViz görselleştirme aracını, Rosbridge'i ve Python kontrolcüsünü aynı anda başlatacaktır.

### **Adım 2: Web Arayüzünü Başlatın**

Web arayüzünü başlatmak için başka bir terminal açın ve aşağıdaki adımları izleyin:

1. Web arayüzü dizinine gidin:

```bash id="9k9knu"
# Terminal 2
cd ~/ros2_ws/src/ev_robot_description/web_ui
```

2. Web arayüzünü başlatın:

```bash id="0y7cv7"
npm start
```

Tarayıcınız otomatik olarak `http://localhost:3000` adresine gidecektir ve web arayüzü üzerinden robotunuzu kontrol edebilirsiniz.

### **Adım 3: Kontrol Edin!**

Web panelinde **"SİSTEM ÇEVRİMİÇİ"** yazısını gördükten sonra:

* **"Otonom Devriye"** butonuna basarak robotu tura çıkarabilirsiniz.
* **Oda butonlarını** kullanarak robotu spesifik noktalara gönderebilirsiniz.

---

### **📂 Dosya Yapısı**

Proje dosya yapısı şu şekilde düzenlenmiştir:

```plaintext
ev_robot_description/
├── launch/             # Başlatma dosyaları (hepsini_baslat.launch.py)
├── maps/               # Oluşturulan ev haritası (.yaml / .pgm)
├── urdf/               # Robotun 3D modeli ve fiziksel özellikleri
├── worlds/             # Gazebo ev ortamı (.sdf)
├── ev_robot_description/ # Python kontrol kodları (app_kontrol.py)
└── web_ui/             # React Web Uygulaması kaynak kodları
```

Bu yapının her bir bölümünde proje için gerekli olan dosyalar bulunmaktadır. Başlatma dosyaları, haritalar, robot model dosyaları ve web arayüzü kaynak kodları burada yer alır.


İşte istediğiniz şekilde düzenlenmiş "Notlar" kısmı:

```markdown
### 💡 Notlar

- **İlk Başlangıç:** Robotun haritadaki konumu kod tarafından otomatik olarak ayarlanır (Initial Pose). Ancak robot hareket etmezse, RViz üzerinden manuel olarak "2D Pose Estimate" yaparak robotun konumunu güncelleyebilirsiniz.

- **Mobil Kontrol:** Telefondan kontrol etmek için bilgisayar ve telefonun aynı Wi-Fi ağında olması ve localhost yerine bilgisayarın IP adresinin (örn: `192.168.1.XX:3000`) kullanılması gerekir.
```
