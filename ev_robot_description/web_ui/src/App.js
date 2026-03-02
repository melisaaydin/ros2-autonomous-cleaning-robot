import React, { useState, useEffect } from 'react';
import * as ROSLIB from 'roslib'; 
import './App.css';

function App() {
  const [connected, setConnected] = useState(false);
  const [ros, setRos] = useState(null);
  const [status, setStatus] = useState("Bağlanıyor...");

  useEffect(() => {
    // ROS Bağlantısını Kurma
    const rosObj = new ROSLIB.Ros({
      url: 'ws://localhost:9090' 
    });

    rosObj.on('connection', () => {
      console.log('Bağlantı başarılı!');
      setConnected(true);
      setStatus("SİSTEM ÇEVRİMİÇİ");
    });

    rosObj.on('error', (error) => {
      console.log('Hata:', error);
      setConnected(false);
      setStatus("BAĞLANTI HATASI");
    });

    rosObj.on('close', () => {
      console.log('Kapandı.');
      setConnected(false);
      setStatus("BAĞLANTI KESİLDİ");
    });

    setRos(rosObj);
  }, []);

  const komutGonder = (veri) => {
    if (ros) {
      const cmdTopic = new ROSLIB.Topic({
        ros: ros,
        name: '/app_komut',
        messageType: 'std_msgs/String'
      });

      const msg = { data: veri }; 
      
      cmdTopic.publish(msg);
      console.log("Komut gönderildi:", veri);
    }
  };

  return (
    <div className="dashboard">
      <header className="header">
        <h1>EV ROBOTU KONTROL MERKEZİ</h1>
        <div className={`status-badge ${connected ? 'online' : 'offline'}`}>
          <div className="dot"></div>
          {status}
        </div>
      </header>

      <main className="control-panel">
        <section className="card operations">
          <h2>Operasyon</h2>
          <div className="button-grid">
            <button className="btn btn-primary" onClick={() => komutGonder('devriye')} disabled={!connected}>
              🚀 OTONOM DEVRİYE
            </button>
            <button className="btn btn-danger" onClick={() => komutGonder('dur')} disabled={!connected}>
              🛑 ACİL DURDUR
            </button>
          </div>
        </section>

        <section className="card locations">
          <h2>Hedef Seçimi</h2>
          <div className="button-grid-small">
            <button className="btn btn-secondary" onClick={() => komutGonder('salon')} disabled={!connected}>🛋️ Salon</button>
            <button className="btn btn-secondary" onClick={() => komutGonder('mutfak')} disabled={!connected}>🍽️ Mutfak</button>
            <button className="btn btn-secondary" onClick={() => komutGonder('yatak')} disabled={!connected}>🛏️ Yatak Odası</button>
            <button className="btn btn-warning" onClick={() => komutGonder('giris')} disabled={!connected}>🔌 Şarj İstasyonu</button>
          </div>
        </section>
      </main>
      
      <footer className="footer">v1.0 | ROS 2 Jazzy System</footer>
    </div>
  );
}

export default App;