#ifndef MAIN_DRIVE_H
#define MAIN_DRIVE_H
#include <Arduino.h>
#include "MeMegaPi.h"

#define MAX_SPEED 255

class MainDrive
{
private:


    const int setPoint = 3; // 1 left, 5 right, 3 middle

    float kp;
    float ki;
    float kd;
    float i = 0;
    float d = 0;
    float lastE = 0;
    uint8_t defaultSpeed = 255;
    unsigned long softStartTimer = 0;
    unsigned long softStartDuration = 500;
    bool isStopped = false;
    bool invertForward = false;

    int getAndUpdatePos();
    void moveDirection(float direction, uint8_t speed = NULL);
    void handleLeftEncoder();
    void handleRightEncoder();
    void setupEncoders();
    void updateLineFollow();
public:
    static MainDrive* singletonInstance;
    static void pulseCheckLeftEncoder();
    static void pulseCheckRightEncoder();
    static void targetReached(int16_t slot, int16_t exitId);

    MeEncoderOnBoard leftEncoder;
    MeEncoderOnBoard rightEncoder;
    MeLineFollower lineFollowerSensor;

    MainDrive(uint8_t lineSensorPort, uint8_t leftEncoderPort, uint8_t rightEncoderPort);
    void SetupLineFollow(float kp = 0.05, float ki = 0.001, float kd = 0.3, bool inverForward = false);
    void UpdateMainDrive();
    void StopFollowing();
    void ResumeFollowing();
    void SetDefaultSpeed(int newSpeed);
    void Flip();
};

#endif