#include "GripperLib.h"

Gripper::Gripper(uint8_t port, unsigned long timeout)
    : motor(port),
      timeoutMs(timeout),
      lastCommandTime(0),
      gripperState(0) {
}


void Gripper::update() {
    if (millis() - lastCommandTime >= timeoutMs) {
        stop();
    }
}

void Gripper::open() {
    lastCommandTime = millis();
    gripperState = -150;
    motor.run(gripperState);
}

void Gripper::close() {
    lastCommandTime = millis();
    gripperState = 150;
    motor.run(gripperState);
}

void Gripper::stop() {
    gripperState = 0;
    motor.stop();
}