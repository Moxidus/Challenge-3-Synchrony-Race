# Aruco Tracking Module for Dumpster Truck (DT)
# This module will handle all Aruco marker detection and tracking for the Dumpster Truck (DT).

import cv2
import numpy as np
import os
from cv2 import aruco
import math

# configuration parameters
aruco_size = 0.042
aruco_marker_id = 1
aruco_type = cv2.aruco.DICT_4X4_50
aruco_Dict = cv2.aruco.getPredefinedDictionary(aruco_type)
aruco_Params = cv2.aruco.DetectorParameters()

root = os.getcwd()
camera_calibration_data = os.path.join(root, "Main", "fishEyeA53CameraCalibration_fisheye_droidCam.npz")
data = np.load(camera_calibration_data)
cam_Matrix = data["camMatrix"]
dist_Coeff = data["distCoeff"]



def undistort_fisheye(img):
    h, w = img.shape[:2]

    newK = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
        cam_Matrix, dist_Coeff, (w, h), np.eye(3), balance=0.0
    )

    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        cam_Matrix, dist_Coeff, np.eye(3), newK, (w, h), cv2.CV_16SC2
    )

    undistorted = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR)

    return undistorted, newK

# Source - https://stackoverflow.com/a/76802895
# Posted by M lab, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-20, License - CC BY-SA 4.0

def estimatePoseSingleMarkers(corners, marker_size, mtx, distortion):
    '''
    This will estimate the rvec and tvec for each of the marker corners detected by:
       corners, ids, rejectedImgPoints = detector.detectMarkers(image)
    corners - is an array of detected corners for each detected marker in the image
    marker_size - is the size of the detected markers
    mtx - is the camera matrix
    distortion - is the camera distortion matrix
    RETURN list of rvecs, tvecs, and trash (so that it corresponds to the old estimatePoseSingleMarkers())
    '''
    marker_points = np.array([[-marker_size / 2, marker_size / 2, 0],
                              [marker_size / 2, marker_size / 2, 0],
                              [marker_size / 2, -marker_size / 2, 0],
                              [-marker_size / 2, -marker_size / 2, 0]], dtype=np.float32)
    trash = []
    rvecs = []
    tvecs = []
    for c in corners:
        nada, R, t = cv2.solvePnP(marker_points, c, mtx, distortion, False, cv2.SOLVEPNP_IPPE_SQUARE)
        rvecs.append(R)
        tvecs.append(t)
        trash.append(nada)
    return rvecs, tvecs, trash



def arucoPoseEstimation(camMat, distCoeff, img, drawDistance=False):
    # Undistort fisheye
    img, camMat = undistort_fisheye(img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    detector = cv2.aruco.ArucoDetector(aruco_Dict, aruco_Params)
    corners, ids, rejected = detector.detectMarkers(gray)
    
    if ids is None:
        return img, None, None, None, None

    aruco.drawDetectedMarkers(img, corners, ids)

    rvecs, tvecs, _ = estimatePoseSingleMarkers(
        corners, 0.042, camMat, None  # distortion already removed
    )

    for i in range(len(ids)):
        
        if ids[i] != aruco_marker_id:
            continue
        
        tvec = tvecs[i]
        rvec = rvecs[i]
        # print(tvecs)

        
        # 1. Convert rvec to a 3x3 Matrix
        rmat, _ = cv2.Rodrigues(rvec)

        yaw_radians = math.atan2(rmat[1, 0], rmat[0, 0])
        pitch_radians = math.atan2(-rmat[2, 0], math.sqrt(rmat[2, 1]**2 + rmat[2, 2]**2))
        roll_radians = math.atan2(rmat[2, 1], rmat[2, 2])

        yaw_degrees = math.degrees(yaw_radians)
        # Might have to switch roll and pitch depending on whether the tag is on its side
        pitch_degrees = math.degrees(pitch_radians)
        roll_degrees = math.degrees(roll_radians)

        # True distance
        distance = np.linalg.norm(tvec)

        # print(f"Marker ID {ids[i][0]}")
        # print(f"Distance: {distance:.3f} m, XYZ: {tvec}\n")

        if drawDistance:
            # Display distance on image
            text = f"ID {ids[i][0]}: {distance:.3f} m"
            print(corners[0][0][0][0], corners[0][0][0][1])

            cv2.putText(img, text, (int(corners[0][0][0][0]), int(corners[0][0][0][1] - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
            )

        # Draw axes (center of marker)s
        cv2.drawFrameAxes(img, camMat, None, rvecs[i], tvecs[i], 0.05)

        return img, tvec, yaw_degrees, pitch_degrees, roll_degrees
    return img, None
    

class ArucoTracking:
    def __init__(self):
        
        if os.name == "posix":
            self.webcam = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L2)  # A53 camera
        elif os.name == "nt":
            self.webcam = cv2.VideoCapture(1)  # A53 camera
        else:
            raise Exception(f"unsuported os '{os.name}'")
            
        # Initialize Aruco tracking parameters and variables
        pass

    # def start_tracking(self):
    #     # Start the Aruco tracking process
    #     pass  

    # def stop_tracking(self):
    #     # Stop the Aruco tracking process
    #     pass

    def get_marker_position(self):
        ret, img = self.webcam.read()
        
        if not ret:
            raise Exception("Failed to fetch webcam")
        
        return arucoPoseEstimation(cam_Matrix, dist_Coeff, img, True)



# testing

if __name__ == "__main__":
    tracker = ArucoTracking()
    
    while True:
        img, pos = tracker.get_marker_position()
        print(pos)
        cv2.imshow('test ', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    