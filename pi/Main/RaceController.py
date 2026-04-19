# Race Controller
# This is the main controller responsible for managing the race and providing communication with the devices.
# Controlls 2 robots:
# - Dumpster Truck (DT) - Communicates over usb serial
# - Dumpster Fire (DF) - Communicates over BLE Serial


# Required modules to be created:
# - Serial Communication module for DT
# - BLE Communication module for DF
# - Aruco marker detection module using OpenCV


from UsbCommunication import UsbCommunication
from BleCommunication import BleCommunication
from ArucoTracking import ArucoTracking


# configuration parameters
# camera location relative to the center of the robot (x, y, z) in meters
camera_location = [ 0.0, 0.0, 0.0]
gripper_location = [ 0.0, 0.0, 0.0]




### Race stages

## stage 1 - Start

    # wait for DT and DF to be ready

    # wait for start signal from DT

    # send start following the line signal to DT and DF

## stage 2 - reach point A

    # wait for "Reached point A" signals from DT and DF

    # Request DT current location and store it

    # Send command to rotate 90 degrees to the Left to DT

    # Turn on camera and send local coordinates of an Aruco marker to DT every frame

    # wait for "Reached point B" signal from DT

    # check that the location of the Aruco marker is within a certain distance from the location of DT at point A

## stage 3 - the hand over
    # send command to DF to close the gripper

    # wait for "Gripper closed" signal from DF

    # send command to DT to open the gripper

    # wait for "Gripper opened" signal from DT

    # Send command to DT to move back a certain distance

## stage 4 - reach the finish line 
    # Send command to DT to rotate 90 degrees to the Left

    # Send command to DT to follow the line until the finish line is reached

    # Send command to DF to rotate 180 degrees to the Left

    # Send command to DF to follow the line until the finish line is reached

    # wait for "Reached finish line" signal from DT and DF

    # Send command to DT and DF to "Celebrate"


