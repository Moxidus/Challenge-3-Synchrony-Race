import cv2
import numpy as np
import os
from cv2 import aruco


# arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_100)
arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
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
        tvec = tvecs[i][0]

        # True distance
        distance = np.linalg.norm(tvec)

        # print(f"Marker ID {ids[i][0]}")
        print(f"Distance: {distance:.3f} m, XYZ: {tvec}\n")

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


if __name__ == "__main__":

    root = os.getcwd()
    # paramPath = os.path.join(root, "fishEyeA53CameraCalibration_fisheye.npz")
    paramPath = os.path.join(root, "Main", "fishEyeA53CameraCalibration_fisheye_droidCam.npz")

    data = np.load(paramPath)

    camMatrix = data["camMatrix"]
    distCoeff = data["distCoeff"]
    
    cam = cv2.VideoCapture(0)

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
            result = cv2.resize(result, ( height,width))
            cv2.imshow("Webcam", result)
        else:
            width = frame.shape[0]*2
            height = frame.shape[1]*2
            frame = cv2.resize(frame, (height,width))
            cv2.imshow("Webcam", frame)
 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()