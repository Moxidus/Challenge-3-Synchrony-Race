import cv2
import numpy as np
import os
from cv2 import aruco
import math

# arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_100)
arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
arucoParams = cv2.aruco.DetectorParameters()


def undistort_fisheye(img, K, D):
    h, w = img.shape[:2]

    newK = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
        K, D, (w, h), np.eye(3), balance=0.0
    )

    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        K, D, np.eye(3), newK, (w, h), cv2.CV_16SC2
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
    img, camMat = undistort_fisheye(img, camMat, distCoeff)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    detector = cv2.aruco.ArucoDetector(arucoDict, arucoParams)
    corners, ids, rejected = detector.detectMarkers(gray)
    
    # corners, ids, rejected = cv2.aruco.detectMarkers(
    #     gray, arucoDict, parameters=arucoParams
    # )

    if ids is None:
        return None

    aruco.drawDetectedMarkers(img, corners, ids)

    rvecs, tvecs, _ = estimatePoseSingleMarkers(
        corners, 0.042, camMat, None  # distortion already removed
    )

    

    for i in range(len(ids)):
        if ids[i] != 0:
            continue
        
        tvec = tvecs[i]
        rvec = rvecs[i]
        
        # 1. Convert rvec to a 3x3 Matrix
        rmat, _ = cv2.Rodrigues(rvec)

        # 2. Extract Yaw (rotation around the vertical axis)
        # Note: The exact index depends on your coordinate system. 
        # For standard OpenCV camera coords (Z forward, Y down):
        yaw_radians = math.atan2(rmat[1, 0], rmat[0, 0])
        pitch_radians = math.atan2(-rmat[2, 0], math.sqrt(rmat[2, 1]**2 + rmat[2, 2]**2))
        roll_radians = math.atan2(rmat[2, 1], rmat[2, 2])

        # 3. Convert to degrees for sanity check
        yaw_degrees = math.degrees(yaw_radians)
        pitch_degrees = math.degrees(pitch_radians)
        roll_degrees = math.degrees(roll_radians)

        # True distance
        distance = np.linalg.norm(tvec)

        # print(f"Marker ID {ids[i][0]}")
        print(f"Distance: {distance:.3f} m, XYZ: {tvec}, yaw: {yaw_degrees}\, pitch: {pitch_degrees}\, roll: {roll_degrees}\n")
        
        
        plotter.update(roll_degrees, pitch_degrees, yaw_degrees)

        if drawDistance:
            # Display distance on image
            text = f"ID {ids[i][0]}: {distance:.3f} m"
            print(corners[0][0][0][0], corners[0][0][0][1])

            cv2.putText(img, text, (int(corners[0][0][0][0]), int(corners[0][0][0][1] - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
            )

        # Draw axes (center of marker)s
        cv2.drawFrameAxes(img, camMat, None, rvecs[i], tvecs[i], 0.05)

    return img

import matplotlib.pyplot as plt
from collections import deque

class PosePlotter:
    def __init__(self, max_samples=100):
        self.max_samples = max_samples
        self.yaw_data = deque(maxlen=max_samples)
        self.pitch_data = deque(maxlen=max_samples)
        self.roll_data = deque(maxlen=max_samples)
        
        plt.ion()  # Turn on interactive mode
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(8, 6))
        self.fig.tight_layout(pad=3.0)

    def update(self, roll, pitch, yaw):
        self.roll_data.append(roll)
        self.pitch_data.append(pitch)
        self.yaw_data.append(yaw)

        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        self.ax1.plot(self.roll_data, color='r', label='Roll')
        self.ax1.set_ylim([-180, 180])
        self.ax1.legend(loc="upper right")

        self.ax2.plot(self.pitch_data, color='g', label='Pitch')
        self.ax2.set_ylim([-180, 180])
        self.ax2.legend(loc="upper right")

        self.ax3.plot(self.yaw_data, color='b', label='Yaw')
        self.ax3.set_ylim([-180, 180])
        self.ax3.legend(loc="upper right")

        plt.pause(0.001) # Brief pause to allow the UI to update


plotter = PosePlotter(max_samples=50)

if __name__ == "__main__":

    root = os.getcwd()
    # paramPath = os.path.join(root, "fishEyeA53CameraCalibration_fisheye.npz")
    paramPath = os.path.join(root, "Main", "fishEyeA53CameraCalibration_fisheye_droidCam.npz")

    data = np.load(paramPath)

    camMatrix = data["camMatrix"]
    distCoeff = data["distCoeff"]
    
    cam = cv2.VideoCapture(1)

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        result = arucoPoseEstimation(camMatrix, distCoeff, frame, True)

        # scale up for better visibility

        # frame = cv2.resize(frame,  (2,2), fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)

        if result is not None:
            width = result.shape[0]*2
            height = result.shape[1]*2
            # result = cv2.resize(result, ( height,width))
            cv2.imshow("Webcam", result)
        else:
            width = frame.shape[0]*2
            height = frame.shape[1]*2
            # frame = cv2.resize(frame, (height,width))
            cv2.imshow("Webcam", frame)
 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()