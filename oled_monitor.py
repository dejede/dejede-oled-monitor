import time
import subprocess
import random
import json
import urllib.request
from datetime import datetime
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# Inisialisasi I2C OLED 128x64 (Port 1, Alamat I2C umum 0x3C)
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=128, height=64)

connected_since = None
last_status = False
wave_history = [random.randint(5, 25) for _ in range(21)]

public_ip = "Checking..."
last_ip_check = 0

def get_modem_info():
    operator = "NO SIM"
    signal_bars = 0
    band_info = "B--"
    
    try:
        op_out = subprocess.check_output(["uqmi", "-d", "/dev/cdc-wdm0", "--get-serving-system"], stderr=subprocess.STDOUT, universal_newlines=True)
        op_data = json.loads(op_out)
        if "descriptions" in op_data and op_data["descriptions"]:
            operator = op_data["descriptions"][0][:8].upper()
        elif "plmn" in op_data:
            operator = str(op_data["plmn"])[:6]

        sig_out = subprocess.check_output(["uqmi", "-d", "/dev/cdc-wdm0", "--get-signal-info"], stderr=subprocess.STDOUT, universal_newlines=True)
        sig_data = json.loads(sig_out)
        
        rssi = 0
        if "rssi" in sig_data:
            rssi = sig_data["rssi"]
        elif "lte" in sig_data and "rssi" in sig_data["lte"]:
            rssi = sig_data["lte"]["rssi"]
            
        if rssi >= -70:
            signal_bars = 4
        elif rssi >= -85:
            signal_bars = 3
        elif rssi >= -100:
            signal_bars = 2
        elif rssi >= -110:
            signal_bars = 1
        else:
            signal_bars = 0

        if "rsrp" in sig_data or "lte" in sig_data:
            band_info = "LTE"
            
    except Exception:
        operator = "DELL DW"
        signal_bars = 3
        band_info = "B3/B40"
            
    return operator, signal_bars, band_info

def check_internet():
    try:
        output = subprocess.check_output(
            ["ping", "-c", "1", "-W", "2", "8.8.8.8"], 
            stderr=subprocess.STDOUT, 
            universal_newlines=True
        )
        for line in output.split('\n'):
            if 'time=' in line:
                time_str = line.split('time=')[1].split(' ')[0]
                return True, float(time_str)
        return True, 0.0
    except subprocess.CalledProcessError:
        return False, 0.0

def get_public_ip(is_online):
    global public_ip, last_ip_check
    if not is_online:
        return "OFFLINE"
    
    if time.time() - last_ip_check > 300 or public_ip == "Checking...":
        try:
            req = urllib.request.urlopen("https://api.ipify.org", timeout=3)
            public_ip = req.read().decode('utf-8')
            last_ip_check = time.time()
        except:
            public_ip = "No IP"
    return public_ip

def format_uptime(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

print("dejede-oled-monitor Started...")

while True:
    is_online, latency = check_internet()
    operator_name, bars, active_band = get_modem_info()
    ip_pub = get_public_ip(is_online)
    
    if is_online:
        if not last_status:
            connected_since = time.time()
            last_status = True
        
        uptime_duration = time.time() - connected_since
        uptime_str = format_uptime(uptime_duration)
        status_text = "ONLINE"
        new_val = max(5, min(30, int(35 - latency)))
        wave_history.pop(0)
        wave_history.append(new_val)
    else:
        last_status = False
        connected_since = None
        uptime_str = "00:00:00"
        status_text = "OFFLINE"
        ip_pub = "DISCONNECTED"
        wave_history.pop(0)
        wave_history.append(2)

    with canvas(device) as draw:
        # Top Bar (Sinyal, Operator, Band)
        bx = 2
        by = 10
        for i in range(4):
            bar_height = 3 + (i * 2)
            fill_val = 1 if i < bars else 0
            draw.rectangle((bx + (i * 4), by - bar_height, bx + (i * 4) + 2, by), outline=1, fill=fill_val)

        draw.text((18, 1), operator_name[:7], fill=1)
        draw.text((88, 1), f"[{active_band}]", fill=1)
        draw.line((0, 12, 127, 12), fill=1)

        # Middle Section (Grafik & Status Ping)
        start_x = 4
        for i, h in enumerate(wave_history):
            x = start_x + (i * 5)
            draw.rectangle((x, 42 - h, x + 3, 42), fill=1)

        draw.rectangle((26, 45, 102, 57), outline=1)
        if is_online:
            center_text = f"PING: {int(latency)}ms"
        else:
            center_text = f"STATUS: {status_text}"
        draw.text((30, 47), center_text, fill=1)

        # Footer Section (Uptime & IP Global)
        draw.line((0, 59, 127, 59), fill=1)
        draw.text((2, 61), f"Up:{uptime_str}", fill=1)
        draw.text((64, 61), f"IP:{ip_pub}", fill=1)

    time.sleep(3)
