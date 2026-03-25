import cv2, serial, time
import cv2.aruco as aruco
import numpy as np
# A53 approx intrinsics (adjust for your resolution)
frame_size = (4032, 3024)  # Check cap.get(cv2.CAP_PROP_FRAME_WIDTH/HEIGHT)
K = np.array([[4600, 0, frame_size[0]/2],
              [0, 4600, frame_size[1]/2],
              [0, 1, 0]], dtype=np.float32)
dist = np.zeros(5, dtype=np.float32) #Previous 5

 
cap = cv2.VideoCapture('/dev/video1', cv2.CAP_V4L2)  # A53 camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])
 
def main():
	try:
		while True:
			ret, frame = cap.read()
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			if ret:	
				# Choose dictionary (adjust based on your markers)
				aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
				parameters = cv2.aruco.DetectorParameters()
				detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
				 
				# Detect markers
				corners, ids, rejected = detector.detectMarkers(gray)
				 
				# Draw and read results
				if ids is not None:
					print("detecting something")
					aruco.drawDetectedMarkers(frame, corners, ids)
					for i, (corner, id_) in enumerate(zip(corners, ids)):
						print(f"Marker ID: {id_[0]}, Corners: {corner[0]}")  # corner[0] = [[tl, tr, br, bl]]
				cv2.imshow("SHOW!!!!!!", frame)	
			else:
				break
			#Exit on pressing 'q'
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
	finally:
		pass
	
main()


