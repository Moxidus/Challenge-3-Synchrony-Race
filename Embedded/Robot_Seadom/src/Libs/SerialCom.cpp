
#include "SerialCom.h"

SerialCom::SerialCom(SerialMedium medium)
{
    if(medium == BLUETOOTH) {
        serialPort = &Serial1; // Assuming Serial1 is for Bluetooth
    } else {
        serialPort = &Serial; // Assuming Serial is for USB
    }
}


void SerialCom::SetUpSerial()
{
    serialPort->begin(115200);
}

void SerialCom::Update()
{
  HandleCommands();
}

void SerialCom::SendCommand(const String& command)
{
    serialPort->println(command);
}

void SerialCom::HandleCommands()
{
  static String command = "";

  while (serialPort->available())
  {
    char c = serialPort->read();

    if (c == '\n')
    {
    //   Serial.println("Command: " + command);
      onMessageReceived(command);
      command = "";
    }
    else
    {
      command += c;
    }
  }
}