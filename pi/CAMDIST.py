# IF NEEDED 
import cv2
import numpy as np
# Example camera parameters (replace with your calibrated values)
K = np.array([[689.21, 0, 1295.56],
              [0, 690.48, 942.17],
              [0, 0, 1]], dtype=np.float32)
D = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)  # Fisheye distortion coeffs
 
# New camera matrix for output (scale to adjust FOV/zoom)
Knew = K.copy()
Knew[0:2, 0:2] *= 0.6  # Adjust scale (0.4-1.0)
 
# Initialize maps (compute once for efficiency)
DIM = (1280, 720)  # Set your image/video size here (width, height)
map1, map2 = cv2.fisheye.initUndistortRectifyMap(
    K, D, np.eye(3), Knew, DIM, cv2.CV_16SC2
)
 
# For webcam/video stream
cap = cv2.VideoCapture(1)  # 1 for default camera, or 'video.mp4'
 
while True:
    ret, frame = cap.read()
    if not ret:
        break
 
    # Apply remap for correction
    undistorted = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR, 
                            borderMode=cv2.BORDER_CONSTANT)
 
    cv2.imshow('Original', frame)
    cv2.imshow('Fisheye Corrected', undistorted)
 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 
cap.release()
cv2.destroyAllWindows()
