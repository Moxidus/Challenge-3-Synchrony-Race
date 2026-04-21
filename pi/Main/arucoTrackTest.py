

from UsbCommunication import UsbCommunication
from BleCommunication import BleCommunication
from ArucoTracking import ArucoTracking
import asyncio
import cv2
import numpy as np


# configuration parameters
# camera location relative to the center of the robot (x, y, z) in meters
camera_location = [ 0.0, 0.0, 0.0] # + some rotation
gripper_location = [ 0.0, 0.0, 0.0] # + some location
xOffset = -0.16
# xOffset = -276.4346507065348
yOffset = +0.07



async def track():
	## initialization
 
	# retUSB = await DTruckRadio.connect()
	# if not retUSB:
	# 	raise Exception("Failed to connect to DTruck over USB")

	await DTruckRadio.send_command("resetpos")
	await DTruckRadio.send_command("start relpoint 0 0 0")
	await DTruckRadio.send_command("setspeed 100")
 
	await asyncio.sleep(2)
 
	tracker = ArucoTracking()
	
 
	while True:
		img, pos, yaw_degrees, pitch_degrees, roll_degrees = tracker.get_marker_position()
  

		if pos is not None:
			# R_y = np.array([[0, 0, 1],
			# 				[0, 1, 0],
			# 				[-1, 0, 0]])

			# # Perform the rotation
			# v_rotated = R_y @ pos
			# print(v_rotated)	
			print(pos[0])
			x = round(pos[2][0] + xOffset, 4)
			y = -round(pos[0][0] + yOffset, 4)
			theta = roll_degrees * 0
   
			print(f"X: {100*x:.3f} y: {100*y:.3f} ")

			# await asyncio.sleep(1)
			# await DTruckRadio.send_command(f"start relpoint {x} {y} {theta}") # these cordinates will be rotated in the robot
			# await DTruckRadio.send_command(f"getpos")
			# print(DTruckRadio.get_last_response())

   
			
		cv2.imshow('test ', img)
  
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
   
		# await asyncio.sleep(5)
			
   
			
  
			

		# cv2.imshow('test ', img)
  
		# if cv2.waitKey(1) & 0xFF == ord('q'):
		# 	break
    

 
 

    
    
    



DTruckRadio = BleCommunication()


asyncio.run(track())