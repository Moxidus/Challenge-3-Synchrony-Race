import cv2, serial, time
import numpy as np
cap = cv2.VideoCapture(1) 

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)

def pixel(centroid):
	l = f"{centroid}\n"
	ser.write(l.encode("ascii"))

def main():
	try:
		while True:
			ret, frame = cap.read()
			if ret:	
				img = frame[100:101]
				img_G = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				_, newimg = cv2.threshold(img_G, 67, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
				line = newimg.flatten()
				cv2.imshow("", newimg)
				maxLen = 0
				maxIndex = -1
				currLen = 0
				medianLineThickness = 50
				for i,val in enumerate(line):
					if val != 0:
						if abs(currLen - medianLineThickness) < abs(maxLen - medianLineThickness):
							maxIndex = i - currLen
							maxLen = currLen
						currLen = 0
					else:
						currLen += 1
				if abs(currLen - medianLineThickness) < abs(maxLen - medianLineThickness):
					maxIndex = i - currLen
					maxLen = currLen
					
				centroid = maxIndex + 25
				pixel(centroid)
				print(centroid, maxLen)	
			else:
				break
			#Exit on pressing 'q'
			if cv2.waitKey(40) & 0xFF == ord('q'):
				break
	finally:
		pass
	
main()
