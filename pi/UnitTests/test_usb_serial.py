from Main.UsbCommunication import UsbCommunication
import asyncio


class FakeSerial:
    def __init__(self):
        self.written = []
        self.to_read = []
        self.is_open = False
        self.mock_responses = {}
        
    def write(self, data):
        self._check_open()
        if data in self.mock_responses:
            self.to_read += [self.mock_responses[data]]
        self.written.append(data)

    def readline(self):
        self._check_open()
        return self.to_read.pop(0) if self.to_read else b''
    
    def _check_open(self):
        if not self.is_open:
            raise Exception("Serial port is not open")
    
    def close(self):
        self.is_open = False
    
    def open(self):
        self.is_open = True
        
    def set_mock_response(self, command, response):
        self.mock_responses.update({(command + '\n').encode("ascii"): response.encode("ascii")})
        


def test_test_UsbCommunication_Connect():
    fake = FakeSerial()
    usb = UsbCommunication(mockSerial=fake)
    
    # test initial state
    assert not fake.is_open
    
    # test connect and disconnect
    usb.connect()
    assert fake.is_open
    
    usb.disconnect()
    assert not fake.is_open

    

def test_UsbCommunication_SendCommand():
    fake = FakeSerial()
    usb = UsbCommunication(mockSerial=fake)
    usb.connect()

    commandText = "close grip"
    usb.send_command(commandText)
    
    expectedOut = (commandText + '\n').encode("ascii")   
    assert fake.written[0] == expectedOut





def test_UsbCommunication_waitResponse():
    async def run_test():
        fake = FakeSerial()
        usb = UsbCommunication(mockSerial=fake)
        usb.connect()

        fake.set_mock_response("getpos", "pose 1.12 5.66 666")

        usb.send_command("getpos")
        found, response = await usb.wait_for_response("pose", 1)

        assert found
        assert response == "1.12 5.66 666"

    asyncio.run(run_test())
    
    
    