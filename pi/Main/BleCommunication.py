# BLE Communication Module for Dumpster Truck (DT)
# This module will handle all BLE communication with the Dumpster Truck (DT). It will be responsible for sending commands to DT and receiving status updates from DT.

# Available BLE Commands:
# "close grip"            - Closes the gripper
# "open grip"             - Opens the gripper
# "stop track"            - Stops path following
# "start track"           - Resumes path following
# "flip"                  - Executes robot flip
# "celebrate"             - Triggers celebration routine
# "start point <x> <y> <t>" - Sets initial navigation coordinates and theta
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



class BleCommunication:
    def __init__(self):
        # Initialize USB communication parameters and variables
        self.responseBuffer = []

    def connect(self):
        # Establish USB serial connection with the Dumpster Truck (DT)
        pass

    def disconnect(self):
        # Disconnect USB serial connection with the Dumpster Truck (DT)
        pass

    def send_command(self, command):
        # Send a command to the Dumpster Truck (DT) over USB serial
        pass

    def get_last_response(self):
        # Get the last response received from the Dumpster Truck (DT) over USB serial
        pass

    def _handle_incoming_data(self, data):
        # Internal method to handle incoming data from the Dumpster Truck (DT) over USB serial
        # This method should be called whenever new data is received from the serial connection
        self.responseBuffer.append(data)