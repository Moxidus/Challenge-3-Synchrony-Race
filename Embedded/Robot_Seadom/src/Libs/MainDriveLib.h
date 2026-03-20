#ifndef MAIN_DRIVE_H
#define MAIN_DRIVE_H
#include <Arduino.h>
#include "MeMegaPi.h"

class LineFollower
{
private:


    const int setPoint = 3; // 1 left, 5 right, 3 middle

    float kp;
    float ki;
    float kd;
    float i = 0;
    float d = 0;
    float lastE = 0;
    unsigned long softStartTimer = 0;
    unsigned long softStartDuration = 500;
    bool isStopped = false;

    int getPos();
    void moveDirection(float direction, int speed = 255);
    void handleLeftEncoder();
    void handleRightEncoder();
    void setupEncoders();
public:
    static LineFollower* singletonInstance;
    static void pulseCheckLeftEncoder();
    static void pulseCheckRightEncoder();
    static void targetReached(int16_t slot, int16_t exitId);

    MeEncoderOnBoard leftEncoder;
    MeEncoderOnBoard rightEncoder;
    MeLineFollower lineFollowerSensor;

    LineFollower(uint8_t lineSensorPort, uint8_t leftEncoderPort, uint8_t rightEncoderPort);
    void SetupLineFollow(float kp = 0.05, float ki = 0.001, float kd = 0.3);
    void UpdateMainDrive();
    void StopFollowing();
    void ResumeFollowing();
    void Do180();
};

#endif