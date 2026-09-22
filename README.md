# 🚀 dejede-oled-monitor

> Utilitas monitoring koneksi internet *real-time* dengan animasi visual dinamis untuk **Orange Pi Zero 3** ber-OS **OpenWrt**, menggunakan layar **LCD OLED 0.96" I2C (128x64)** dan integrasi modem seluler **Dell DW** (QMI/MBIM).

---

## 📌 Fitur Utama
* **Top Bar (Informasi Seluler):** Menampilkan indikator bar sinyal dinamis, nama operator seluler, dan band frekuensi aktif dari modem Dell DW.
* **Middle Section (Grafik & Latency):** Menampilkan grafik equalizer/gelombang trafik yang bergerak naik-turun secara *real-time* berdasarkan fluktuasi ping internet.
* **Footer Section (Uptime & IP Publik):** Menghitung durasi koneksi aktif (*uptime*) secara kontinu serta menampilkan IP Publik global secara berkala.

---

## 🛠️ Kebutuhan Hardware & Wiring

* **Orange Pi Zero 3** (Running OpenWrt)
* **LCD OLED 0.96" I2C** (Resolusi 128x64, Controller SSD1306)
* **Modem Dell DW** (Terkonfigurasi via QMI/MBIM)
* Kabel Jumper (Female-to-Female)

### Skema Wiring Pin (I2C)
| Pin OLED | Pin Orange Pi Zero 3 |
| :--- | :--- |
| **VCC** | 3.3V |
| **GND** | Ground (GND) |
| **SDA** | I2C SDA Pin |
| **SCL** | I2C SCL Pin |

---

## 📖 Panduan Instalasi (Step-by-Step)

### 1. Update & Install Paket Sistem
Masuk ke terminal OpenWrt Anda melalui SSH, lalu jalankan perintah berikut:
```bash
opkg update
opkg install kmod-i2c-core kmod-i2c-gpio python3 python3-light python3-pip uqmi

---

2. Install Library Python (luma.oled)
Instal dependensi dan library grafis OLED menggunakan pip3:

Bash
opkg install python3-codecs python3-openssl
pip3 install luma.oled
3. Deploy Script Monitoring
Buat file script baru di direktori /root/:

Bash
nano /root/oled_monitor.py
(Salin kode program dari file oled_monitor.py ke dalam editor, lalu simpan dengan menekan Ctrl+O, Enter, lalu keluar menggunakan Ctrl+X).

4. Uji Coba Manual
Pastikan script berjalan dengan baik tanpa error di terminal:

Bash
python3 /root/oled_monitor.py
(Tekan Ctrl+C untuk keluar dari mode uji coba).

5. Konfigurasi Auto-Start (Daemon init.d)
Agar script berjalan otomatis di latar belakang saat Orange Pi Zero 3 melakukan booting:

Buat file service init.d:

Bash
nano /etc/init.d/oled_monitor
Masukkan konfigurasi layanan berikut:

Bash
#!/bin/sh /etc/rc.common

START=99
STOP=10

start() {
    python3 /root/oled_monitor.py &
}

stop() {
    killall python3
}
Berikan izin eksekusi dan aktifkan layanan:

Bash
chmod +x /etc/init.d/oled_monitor
/etc/init.d/oled_monitor enable
/etc/init.d/oled_monitor start
📜 Lisensi
Proyek ini bersifat open-source dan bebas untuk dikembangkan kembali sesuai kebutuhan Anda.
