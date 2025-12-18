# Raspberry Pi Deployment Guide

## Prerequisites

1. Raspberry Pi (3B+ or newer recommended)
2. Raspberry Pi OS Lite (64-bit) installed
3. Internet connection
4. Hardware components:
   - RFID reader (MFRC522)
   - Matrix keypad
   - Thermal printer (ESC/POS compatible)

## Deployment Steps

### 1. Prepare the Code Package

On your development machine, run the preparation script:

```bash
./prepare-pi.bat  # On Windows
```

This creates `rpi-hardware-appliance.zip` for transfer.

### 2. Transfer to Raspberry Pi

```bash
scp rpi-hardware-appliance.zip pi@your-pi-ip:/home/pi/
```

### 3. Setup on Raspberry Pi

SSH into your Raspberry Pi:

```bash
ssh pi@your-pi-ip
```

Extract the package:

```bash
unzip rpi-hardware-appliance.zip
cd rpi-hardware-appliance
```

Run the setup script:

```bash
chmod +x setup-pi.sh
./setup-pi.sh
```

### 4. Hardware Connections

Connect your hardware components:

1. **RFID Reader (MFRC522)**:
   - SDA/SS to SPI CS0 (GPIO 8)
   - SCK to SPI SCLK (GPIO 11)
   - MOSI to SPI MOSI (GPIO 10)
   - MISO to SPI MISO (GPIO 9)
   - GND to Ground
   - VCC to 3.3V

2. **Matrix Keypad**:
   - Connect row pins to GPIO pins (configure in `app/config.py`)
   - Connect column pins to GPIO pins (configure in `app/config.py`)

3. **Thermal Printer**:
   - Connect via USB

### 5. Configure GPIO Pins

Edit `app/config.py` to match your hardware connections:

```bash
nano app/config.py
```

### 6. Add Users

```bash
# Activate virtual environment
source rpi-venv/bin/activate

# Add a user
curl -X POST http://localhost:5000/api/users \
     -H "Content-Type: application/json" \
     -d '{"rfid_uid": "123456789", "pin": "1234"}'
```

### 7. Run the Application

```bash
# Activate virtual environment
source rpi-venv/bin/activate

# Run the application
python3 run.py
```

### 8. Install as System Service (Optional)

```bash
# Copy service file
sudo cp rpi-hardware-appliance.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable the service
sudo systemctl enable rpi-hardware-appliance

# Start the service
sudo systemctl start rpi-hardware-appliance

# Check status
sudo systemctl status rpi-hardware-appliance
```

## Troubleshooting

### Externally Managed Environment Error

Always use the virtual environment:

```bash
source rpi-venv/bin/activate
```

### Permission Denied on GPIO

Add your user to the GPIO group:

```bash
sudo usermod -a -G gpio pi
```

### SPI Not Enabled

Enable SPI using raspi-config:

```bash
sudo raspi-config
# Interfacing Options -> SPI -> Yes
```

Reboot after enabling SPI.