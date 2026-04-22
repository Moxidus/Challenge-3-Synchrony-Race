# BLE Communication Module for Fire Truck (FT) == Daughtership?
# This module will handle all BLE communication with the Firer Truck (FT). It will be responsible for sending commands to FT and receiving status updates from DT and FT.

import asyncio
import time
from bleak import BleakClient, BleakScanner
 
# DEVICE_NAME = "Makeblock_LE001b1068770a"   # DaughterShip BLE adress
RX_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"  # notify/read incoming
TX_UUID = "0000ffe3-0000-1000-8000-00805f9b34fb"  # write outgoing
 
write_lock = asyncio.Lock()

def on_message(sender, data: bytearray):
    text = data.decode("utf-8", errors="replace").strip()
    # print(f"\nRX> {text}")
 
async def safe_write(client: BleakClient, message: str):
    async with write_lock:
        payload = (message + "\n").encode("utf-8")
 
        # Try write-with-response first because it prevents overlapping writes better.
        # If the characteristic does not support it, fall back to write-without-response.
        try:
            await client.write_gatt_char(TX_UUID, payload, response=True)
        except Exception:
            await client.write_gatt_char(TX_UUID, payload, response=False)
            await asyncio.sleep(0.15)
         
class BleCommunication:
    def __init__(self, deviceName = "Makeblock_LE001b1068770a"):
        self.DeviceNameBLE = deviceName
        
        self.client = None
        self.responseBuffer = []

    def _on_message(self, sender, data: bytearray):
        text = data.decode("utf-8", errors="replace").strip()
        # print(f"\nRX> {text}")
        self._handle_incoming_data(text)

    async def connect(self): 
        print(f"Scanning for {self.DeviceNameBLE!r}...")
        device = await BleakScanner.find_device_by_name(self.DeviceNameBLE, timeout=10.0)
        if not device:
            print("Device not found")
            return False
        self.client = BleakClient(device)
        await self.client.connect()
        await self.client.start_notify(RX_UUID, self._on_message)
        print("Connected:", self.client.is_connected)
        return True

    async def disconnect(self):
        try:
            await self.client.stop_notify(RX_UUID)
            await self.client.disconnect()
        except Exception:
            pass

    async def send_command(self, command):
        try:
            await safe_write(self.client, command)
        except Exception as e:
            print("Write failed:", repr(e))

    def _handle_incoming_data(self, data):
        self.responseBuffer.append(data)

    def get_last_response(self):
        if not self.responseBuffer:
            return None
        return self.responseBuffer.pop(0)  # FIFO
    
    async def wait_for_command(self, command, timeout=0):
        """Wait until a specific command is received. Default timeout is 10000 seconds."""
        if timeout == 0:
            timeout = 10000

        start_time = time.time()

        while time.time() - start_time < timeout:
            if not self.responseBuffer:
                await asyncio.sleep(0.1)
                continue

            last_command = self.get_last_response()
            print("got command", last_command)
            print("comparing against", command)
            if last_command == command:
                return True

        return False  # timeout

    async def wait_for_response(self, command, timeout=0):
        """Wait until a response starting with command is received. Default timeout is 10000 seconds."""
        if timeout == 0:
            timeout = 10000

        start_time = time.time()

        while time.time() - start_time < timeout:
            if not self.responseBuffer:
                await asyncio.sleep(0.1)
                continue

            last_command = self.get_last_response()
            if last_command.startswith(command):
                args = last_command.replace(command + " ", "", 1).strip()
                return (True, args)

        return (False, None)  # timeout
