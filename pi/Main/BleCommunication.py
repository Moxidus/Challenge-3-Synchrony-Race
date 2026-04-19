# BLE Communication Module for Dumpster Truck (DT)
# This module will handle all BLE communication with the Dumpster Truck (DT). It will be responsible for sending commands to DT and receiving status updates from DT.

import asyncio
import time
from bleak import BleakClient, BleakScanner
 
DEVICE_NAME = "Makeblock_LE001b1068770a"
RX_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"  # notify/read incoming
TX_UUID = "0000ffe3-0000-1000-8000-00805f9b34fb"  # write outgoing
 

class BleCommunication:
    def __init__(self):
        # Initialize BLE communication parameters and variables
        self.responseBuffer = []
        self.client = None

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
                args = lastCommand.replace(command + " ")
                return (True, args)
            
        return (False, None) # timeout


    def _handle_incoming_data(self, data):
        self.responseBuffer.append(data)