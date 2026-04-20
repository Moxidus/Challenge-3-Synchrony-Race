# USB Communication Module for Dumpster Truck (DT)
# This module will handle all USB serial communication with the Dumpster Truck (DT). It will be responsible for sending commands to DT and receiving status updates from DT.

import time
import asyncio
import serial


class UsbCommunication:
    def __init__(self):
        # Initialize USB communication parameters and variables
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)
        self.responseBuffer = []
    def connect(self):
        # Establish USB serial connection with the Dumpster Truck (DT)
        if not ser.is_open:
            ser.open()

    def disconnect(self):
        # Disconnect USB serial connection with the Dumpster Truck (DT)
        if ser.is_open:
            ser.close()

    def send_command(self, command):
        # Send a command to the Dumpster Truck (DT) over USB serial
        Cmd_line = "{command}\n"
	    ser.write(l.encode("ascii"))

    def get_last_response(self) -> str:
        # Get the last response received from the Dumpster Truck (DT) over USB serial
        if not any(self.responseBuffer):
            return None
        
        return self.responseBuffer.pop()

    
    async def wait_for_command(self, command, timeout = 0):
        "default timeout is 10000 seconds"
        if timeout == 0:
            timeout = 10000

        startTime = time.time()

        while time.time() - startTime < timeout:
            if not any(self.responseBuffer):
                await asyncio.sleep(0.1)
                continue
            
            lastCommand = self.get_last_response()
            if lastCommand == command:
                return True
            
        return False # timeout
    
    
    async def wait_for_response(self, command, timeout = 0):
        "default timeout is 10000 seconds"
        if timeout == 0:
            timeout = 10000

        startTime = time.time()

        while time.time() - startTime < timeout:
            if not any(self.responseBuffer):
                await asyncio.sleep(0.1)
                continue
            
            lastCommand = self.get_last_response()
            if lastCommand == command:
                args = lastCommand.replace(command + " ", "")
                return (True, args)
            
        return (False, None) # timeout


    
    def _handle_incoming_data(self, data):
        # Internal method to handle incoming data from the Dumpster Truck (DT) over USB serial
        # This method should be called whenever new data is received from the serial connection
        self.responseBuffer.append(data)


# testing code
if __name__ == "__main__":
    usbComm = UsbCommunication()
    usbComm._handle_incoming_data("TEST_COMMAND ARG1 ARG2")
    print(usbComm.get_last_response()) # should print "TEST_COMMAND ARG1 ARG2"
    asyncio.run(usbComm.wait_for_command("TEST_COMMAND")) # should return True
