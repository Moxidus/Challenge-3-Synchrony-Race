import cv2, time
import cv2.aruco as aruco
import numpy as np
import asyncio
from bleak import BleakClient, BleakScanner
 
DEVICE_NAME = "Makeblock_LE001b1069005f"
RX_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"  # notify/read incoming
TX_UUID = "0000ffe3-0000-1000-8000-00805f9b34fb"  # write outgoing
 
write_lock = asyncio.Lock()
# A53 approx intrinsics (adjust for your resolution)
frame_size = (4032, 3024)  # Check cap.get(cv2.CAP_PROP_FRAME_WIDTH/HEIGHT)
K = np.array([[4600, 0, frame_size[0]/2],
			  [0, 4600, frame_size[1]/2],
			  [0, 1, 0]], dtype=np.float32)
dist = np.zeros(5, dtype=np.float32) #Previous 5
	 
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

	 
cap = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L2)  # A53 camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])

posX = 515		#FOR NOW - NO ACTUAL STAND FOR PHONE
posY = 203
	 
def on_message(sender, data: bytearray):
    text = data.decode("utf-8", errors="replace").strip()
    print(f"\nRX> {text}")
 
async def safe_write(client: BleakClient, message: str):
    async with write_lock:
        payload = (message + "\n").encode("utf-8")
 
        # Try write-with-response first because it prevents overlapping writes better.
        # If the characteristic does not support it, fall back to write-without-response.
        try:
            await client.write_gatt_char(TX_UUID, payload, response=True)
        except Exception:
            await client.write_gatt_char(TX_UUID, payload, response=False)

	
async def main():
	print(f"Scanning for {DEVICE_NAME!r}...")
	device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10.0)
	
	if not device:
		print("Device not found")
		return
 
	print("Found:", device.name, device.address)
 
	async with BleakClient(device) as client:
		print("Connected:", client.is_connected)
		
        # Make sure services are discovered on this connection
		_ = client.services
		await client.start_notify(RX_UUID, on_message)
		print("Listening. Type commands, or 'exit' to quit.")
		while True:
			ret, frame = cap.read()
			if not ret: 
				break
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			
			corners, ids, _ = detector.detectMarkers(gray)
			cv2.imshow("", gray)
			msg = ""
			try:
				if ids is not None:
					for i, marker_id in enumerate((ids.flatten())):
						aruco.drawDetectedMarkers(frame, corners)
						x, y = map(int, corners[i][0][3])  #Corners [] [0 to 3]
						
						if x != None:
							ERRx = x - posX
							ERRy = posY - y
							msg = await safe_write(client, f'point {ERRx} {ERRy}')
							msg = msg.strip()
							
			except:
				print("None")
				
							
		try:
			await client.stop_notify(RX_UUID)
		except Exception:
			pass
     
 
if __name__ == "__main__":
    asyncio.run(main())

