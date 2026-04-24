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
 
 
	retBLE = await DFireRadio.connect()
	if not retBLE:
		raise Exception("Failed to connect to DFire over BLE")
 
	retUSB = await DTruckRadio.connect()
	if not retUSB:
		raise Exception("Failed to connect to DTruck over USB")
 


	## stage 1 - Start

	# # wait for DTruck and DFire to be ready
	# if not await DTruckRadio.wait_for_command("ready"):
	# 		print("timeout while waiting for DTruck to be ready")

	# if not await DFireRadio.wait_for_command("ready"):
	# 		print("timeout while waiting for DFire to be ready")
 
	print("Reseting position")
	await DTruckRadio.send_command("resetpos")
	await DFireRadio.send_command("resetpos")
 
	print("Setting slow speed")
	await DTruckRadio.send_command("setspeed 50")
	await DFireRadio.send_command("setspeed 50")
 
 
	print("current position")
	await DTruckRadio.send_command("getpos")



	print("waiting for start position")
	# wait for start signal from DT
	if not await DFireRadio.wait_for_command("start"):
		print("timeout while waiting for DTruck to be start")
   
   
	await DTruckRadio.send_command("lin down")
	await asyncio.sleep(3.5)
    
    
	await DTruckRadio.send_command("close grip")
	await asyncio.sleep(3.5)
 
 
	await DTruckRadio.send_command("lin mid")
	await asyncio.sleep(3.5)
    
   
   
	print(">>> Starting line following")
	# send start following the line signal to DTruck and DF

 
	await DTruckRadio.send_command("start track")
	await DFireRadio.send_command("start track")
 
	await asyncio.sleep(1)
	print("Setting slow speed")
	await DTruckRadio.send_command("setspeed 150")
	await DFireRadio.send_command("setspeed 150")

	## stage 2 - reach point A


	if not await DFireRadio.wait_for_command("reached A"):
			print("timeout while waiting for DFire to reach A")
	print("DF reached the goal")

	# wait for "Reached point A" signals from DTruck and DF
	if not await DTruckRadio.wait_for_command("reached A"):
			print("timeout while waiting for DTruck to reach A")
	print("DT reached the goal")

	# Request DTruck current location and store it
	# await DTruckRadio.send_command("getpos")
	# success, lineLocation = await DTruckRadio.wait_for_response("getpos") # TODO: THIS IS DEFFINETLY NOT RIGHT!!! FIX
	# print(success, "position", lineLocation )

	# if not success:
	# 	print("timeout while waiting for DFire to get position")

	# Send command to rotate 90 degrees to the Left to DTruck
	await DTruckRadio.send_command("rotate 76")
	await asyncio.sleep(2)
 
 
 # the PARKING STAGE -------------------------------------------------------- START
	await DTruckRadio.send_command("resetpos")
 
	
	# await DTruckRadio.send_command("move 400")
	# await asyncio.sleep(4)
 
	# Turn on camera and send local coordinates of an Aruco marker to DTruck every frame
	arucoTracking = ArucoTracking()

	img, pos, yaw_degrees, pitch_degrees, roll_degrees = arucoTracking.get_marker_position()
 
	xOffset = -0.16
	yOffset = -0.05
 
	x = round(pos[2][0] + xOffset, 4)
	y = -round(pos[0][0] + yOffset, 4)
	theta = roll_degrees * 0

 
	await DTruckRadio.send_command(f"start relpoint {x} {y} {theta}") # these cordinates will be rotated in the robot
	await asyncio.sleep(5)

 # the PARKING STAGE -------------------------------------------------------- END
 
	
	await DFireRadio.send_command("close grip")
	await asyncio.sleep(3.5)
 
    
	await DTruckRadio.send_command("open grip")
	await asyncio.sleep(3.5)
 
 
 

 
	await DTruckRadio.send_command("move -400")
	await asyncio.sleep(4)
 
 
 
	await DTruckRadio.send_command("rotate 110")
	await asyncio.sleep(4)
 
 
	await DFireRadio.send_command("rotate 200")
	await asyncio.sleep(4)
 
 
	await DFireRadio.send_command("setHome")
	await DTruckRadio.send_command("setHome")
 
 
	await DTruckRadio.send_command("start track")
	# await asyncio.sleep(4)
 
 
	await DFireRadio.send_command("setspeed 50")
	await DFireRadio.send_command("start track")
	await asyncio.sleep(2)
 
 
	await DFireRadio.send_command("setspeed 150")
	await DFireRadio.send_command("start track")
	await asyncio.sleep(5)
 
 
	await asyncio.sleep(5000)

	# Turn on camera and send local coordinates of an Aruco marker to DTruck every frame
	arucoTracking = ArucoTracking()

	img, pos, yaw_degrees, pitch_degrees, roll_degrees = arucoTracking.get_marker_position()

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



# DTruckRadio = UsbCommunication()
DTruckRadio = BleCommunication(deviceName="Makeblock_LE001b1069005f")
DFireRadio = BleCommunication(deviceName="Makeblock_LE001b1068770a")


asyncio.run(race())