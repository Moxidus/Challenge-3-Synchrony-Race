# Race Controller
# This is the main controller responsible for managing the race and providing communication with the devices.
# Controlls 2 robots:
# - Dumpster Truck (DTruck) - Communicates over usb serial
# - Dumpster Fire (DFire) - Communicates over BLE Serial


# Available Serial Commands:
# "close grip"            - Closes the gripper
# "open grip"             - Opens the gripper
# "stop track"            - Stops path following
# "start track"           - Resumes path following
# "flip"                  - Executes robot flip
# "celebrate"             - Triggers celebration routine
# "start point <x> <y> <t>" - Sets initial navigation coordinates (meters) and theta (deg)
# "stop point"            - Stops navigation to point
# "vel <v> <omega>"       - Sets linear (v) and angular (omega) velocity
# "point <x> <y>"         - Moves robot to specific XY coordinates
# "move <steps>"          - Moves drive forward by steps
# "rotate <steps>"        - Rotates drive by steps
# "setspeed <val>"        - Sets default movement speed
# "getencoders"           - Returns left and right encoder positions
# "getpos"                - Returns current X, Y, and Theta
# "resetpos"              - Resets X, Y, and Theta to zero

# Dumpster Truck only commands:
# "lin home"              - [Dumpster Truck] Moves linear motor to home
# "lin down"              - [Dumpster Truck] Moves linear motor down
# "linmove <val>"         - [Dumpster Truck] Moves linear motor to specific position


# Required modules to be created:
# - Serial Communication module for DT
# - BLE Communication module for DF
# - Aruco marker detection module using OpenCV


from UsbCommunication import UsbCommunication
from BleCommunication import BleCommunication
from ArucoTracking import ArucoTracking
import asyncio


# configuration parameters
# camera location relative to the center of the robot (x, y, z) in meters
camera_location = [ 0.0, 0.0, 0.0] # + some rotation
gripper_location = [ 0.0, 0.0, 0.0] # + some location



async def race():
	## initialization
 
	retUSB = await DTruckRadio.connect()
	if retUSB:
		raise Exception("Failed to connect to DTruck over USB")
 
	retBLE = await DFireRadio.connect()
	if retBLE:
		raise Exception("Failed to connect to DFire over BLE")


	## stage 1 - Start

	# wait for DTruck and DFire to be ready
	if not await DTruckRadio.wait_for_command("ready"):
			print("timeout while waiting for DTruck to be ready")

	if not await DFireRadio.wait_for_command("ready"):
			print("timeout while waiting for DFire to be ready")

	# wait for start signal from DT
	if not await DTruckRadio.wait_for_command("start"):
			print("timeout while waiting for DTruck to be start")

	# send start following the line signal to DTruck and DF
	DTruckRadio.send_command("start")
	DFireRadio.send_command("start")

	## stage 2 - reach point A

	# wait for "Reached point A" signals from DTruck and DF
	if not await DTruckRadio.wait_for_command("reached A"):
			print("timeout while waiting for DTruck to reach A")

	if not await DFireRadio.wait_for_command("reached A"):
			print("timeout while waiting for DFire to reach A")

	# Request DTruck current location and store it
	DTruckRadio.send_command("getpos")
	success, lineLocation = DTruckRadio.wait_for_response("getpos") # TODO: THIS IS DEFFINETLY NOT RIGHT!!! FIX

	if not success:
		print("timeout while waiting for DFire to reach A")        

	# Send command to rotate 90 degrees to the Left to DTruck
	DTruckRadio.send_command("rotate 90")
	await asyncio.sleep(2)

	# Turn on camera and send local coordinates of an Aruco marker to DTruck every frame
	arucoTracking = ArucoTracking()

	img, arucoPosCameraFrame = arucoTracking.get_marker_position()
	# TODO: convert arucoPosCameraFrame to global coordinates using camera_location and lineLocation and send to DTruck

	# wait for "reached point B" signal from DTruck
	if not await DTruckRadio.wait_for_command("reached B"):
			print("timeout while waiting for DTruck to reach B")

	# check that the location of the Aruco marker is within a certain distance from the location of DTruck at point A
	# TODO: do the check by making sure the tracker position is correct to within some margin of error 

	## stage 3 - the hand over
	# send command to DFire to close the gripper
	DFireRadio.send_command("close grip")

	# wait for "Gripper closed" signal from DFire
	if not await DFireRadio.wait_for_command("gripper closed"):
			print("timeout while waiting for DFire to close gripper")

	# send command to DTruck to open the gripper
	DTruckRadio.send_command("open grip")

	# wait for "Gripper opened" signal from DT
	if not await DTruckRadio.wait_for_command("gripper open"):
			print("timeout while waiting for DTruck to open gripper")

	# Send command to DTruck to move back a certain distance
	DTruckRadio.send_command("move -500")

	await asyncio.sleep(2)

	## stage 4 - reach the finish line 
	# Send command to DTruck to rotate 90 degrees to the Left
	DTruckRadio.send_command("rotate 90")

	# Send command to DFire to rotate 180 degrees to the Left
	DFireRadio.send_command("rotate 180")
	await asyncio.sleep(2)

	# Send command to DFire to follow the line until the finish line is reached
	DFireRadio.send_command("start track")

	# TODO: there is going to be need for line seeking protocol
	# send command to move to last known line pos
	DTruckRadio.send_command("start point " + lineLocation)


	if not await DTruckRadio.wait_for_command("start point reached"):
			print("timeout while waiting for 'start point reached'")

	# Send command to DTruck to follow the line until the finish line is reached
	DTruckRadio.send_command("start track")


	# wait for "Reached finish line" signal from DTruck and DFire
	if not await DTruckRadio.wait_for_command("reached C"):
			print("timeout while waiting for DTruck to reach C")

	if not await DFireRadio.wait_for_command("reached C"):
			print("timeout while waiting for DFire to reach C")

	# Send command to DTruck and DFire to "Celebrate"
	await asyncio.sleep(2)
	DFireRadio.send_command("celebrate")
	DTruckRadio.send_command("celebrate")



DTruckRadio = UsbCommunication()
DFireRadio = BleCommunication()


asyncio.run(race())