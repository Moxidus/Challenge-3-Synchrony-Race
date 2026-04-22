#ifndef GRIPPER_H
#define GRIPPER_H

#include "MeMegaPi.h"
#include <Arduino.h>

class Gripper {
public:
    Gripper(uint8_t port, unsigned long timeout = 3000);

    void update();
    void open();
    void close();
    void stop();

private:
    MeMegaPiDCMotor motor;
    unsigned long timeoutMs;
    unsigned long lastCommandTime;
    int16_t gripperState;
};

#endif