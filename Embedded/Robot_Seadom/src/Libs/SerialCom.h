#ifndef SERIAL_COM_H
#define SERIAL_COM_H

#include <Arduino.h>

class SerialCom {
    enum SerialMedium {
        BLUETOOTH,
        USB
    };
public:
    SerialCom(SerialMedium medium = BLUETOOTH);
    void SetUpSerial();
    void Update();
    void SendCommand(const String& command);

private:
    HardwareSerial *serialPort;

    void (*onMessageReceived)(const String& message) = nullptr;
    void HandleCommands();
    
};

#endif