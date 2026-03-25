import serial, time
PORT = "/dev/ttyUSB0"
BAUD = 9600
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(1)


def send_packet(v1, v2):
	#Clamp 0-100
	v1 = max(0, min(100, int(v1)))
	v2 = max(0, min(100, int(v2)))
	print("Processing...")
	line = f"{v1},{v2}\n"
	ser.write(line.encode("ascii"))
	print("Tried to send")
	
for i in range(0,100): 
	send_packet(100, 100)
	time.sleep(0.1)
print("Message sent")
