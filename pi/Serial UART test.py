import serial
import time

# Open UART at 115200 baud
ser = serial.Serial(
    port='/dev/ttyAMA0',
    baudrate=115200,
    timeout=1
)

while True:
    ser.write(b'Hello UART!\n')
    time.sleep(1)

    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8', errors='ignore')
        print("Received:", data)
