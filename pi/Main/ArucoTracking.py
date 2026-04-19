# Aruco Tracking Module for Dumpster Truck (DT)
# This module will handle all Aruco marker detection and tracking for the Dumpster Truck (DT).

import cv2
import numpy as np
import os
from cv2 import aruco


# configuration parameters
aruco_size = 0.042
aruco_marker_id = 0
aruco_type = cv2.aruco.DICT_4X4_1000
aruco_Dict = cv2.aruco.getPredefinedDictionary(aruco_type)
aruco_Params = cv2.aruco.DetectorParameters()

root = os.getcwd()
camera_calibration_data = os.path.join(root, "fishEyeA53CameraCalibration_fisheye_droidCam.npz")
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


class ArucoTracking:
    def __init__(self):
        self.webcam = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L2)  # A53 camera
        # Initialize Aruco tracking parameters and variables
        pass

    def start_tracking(self):
        # Start the Aruco tracking process
        pass

    def stop_tracking(self):
        # Stop the Aruco tracking process
        pass

    def get_marker_position(self):
        # Return the current position of the detected Aruco marker
        pass