# USB Communication Module for Dumpster Truck (DT)
# This module will handle all USB serial communication with the Dumpster Truck (DT). It will be responsible for sending commands to DT and receiving status updates from DT.

import time
import asyncio
import serial
import threading

class UsbCommunication:
    def __init__(self, mockSerial=None):
        # Initialize USB communication parameters and variables
        self.ser = mockSerial or serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        self.responseBuffer = []
        self._read_thread = None
        self._running = False

    def connect(self):
        # Establish USB serial connection with the Dumpster Truck (DT)
        if not self.ser.is_open:
            self.ser.open()
        # Start background thread to continuously read incoming data
        self._running = True
        self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._read_thread.start()
        return True

    def disconnect(self):
        # Disconnect USB serial connection with the Dumpster Truck (DT)
        self._running = False
        if self.ser.is_open:
            self.ser.close()

    def send_command(self, command):
        # Send a command to the Dumpster Truck (DT) over USB serial
        cmd_line = f"{command}\n"
        self.ser.write(cmd_line.encode("ascii"))

    def get_last_response(self) -> str:
        # Get the oldest response received from the Dumpster Truck (DT) over USB serial — FIFO order
        if not self.responseBuffer:
            return None
        return self.responseBuffer.pop(0)

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

    def _read_loop(self):
        # Background thread: continuously reads lines from the serial port
        while self._running and self.ser.is_open:
            try:
                line = self.ser.readline()
                if line:
                    decoded = line.decode("ascii", errors="replace").strip()
                    if decoded:
                        self._handle_incoming_data(decoded)
            except serial.SerialException:
                print("Serial connection lost.")
                self._running = False
                break

    def _handle_incoming_data(self, data):
        # Internal method to handle incoming data from the Dumpster Truck (DT) over USB serial
        self.responseBuffer.append(data)


# Testing code
if __name__ == "__main__":
    usbComm = UsbCommunication()
    usbComm._handle_incoming_data("TEST_COMMAND ARG1 ARG2")
    print(usbComm.get_last_response())                           # should print "TEST_COMMAND ARG1 ARG2"
    print(asyncio.run(usbComm.wait_for_command("TEST_COMMAND"))) # should return False (buffer now empty after pop)
