import cv2
import cv2.aruco as aruco
import numpy as np
 
# A53 approx intrinsics (adjust for your resolution)
frame_size = (4032, 3024)  # Check cap.get(cv2.CAP_PROP_FRAME_WIDTH/HEIGHT)
K = np.array([[4600, 0, frame_size[0]/2],
              [0, 4600, frame_size[1]/2],
              [0, 1, 0]], dtype=np.float32)
dist = np.zeros(5, dtype=np.float32) #Previous 5
 
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

 
cap = cv2.VideoCapture('/dev/video1', cv2.CAP_V4L2)  # A53 camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])
 
while True:
    ret, frame = cap.read()
    if not ret: break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
    corners, ids, _ = detector.detectMarkers(gray)
    if ids is not None:
 
        for i, (corners_i) in enumerate(zip(corners)):
            aruco.drawDetectedMarkers(frame, corners)

            cv2.putText(frame, f'ID: {ids:.2f}m', 
                       (int(corners_i[0][0][0]), int(corners_i[0][0][1]-10)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
 
    cv2.imshow('ArUco Distance (A53)', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break
 
cap.release()
cv2.destroyAllWindows()
