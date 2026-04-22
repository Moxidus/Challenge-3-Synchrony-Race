#ifndef MAIN_DRIVE_H
#define MAIN_DRIVE_H
#include <Arduino.h>
#include "MeMegaPi.h"

#define MAX_SPEED 255


/*

#ifdef DAUGHTER_ROBOT
// TODO: MEASURE THESE VALUES FOR THE MOTHER ROBOT and calibrate the adjustments to make it go straight and turn the correct amount when it should
#define WHEEL_BASE 165
#define WHEEL_RADIUS 32
#define WHEEL_RADIUS_ADJUSTMENT 1.0 // this includes gear ration and encoder resolution
#define WHEEL_BASE_ADJUSTMENT (0.4823989508)// adjust this to make the robot turn the correct amount when it should
#define GEAR_RATIO 46.0 // adjust this to make the robot go the correct distance when it should
#define ENCODER_RESOLUTION 8 // 8, 12 or 22 pulses check
#define STEPS_PER_REVOLUTION (GEAR_RATIO * ENCODER_RESOLUTION)
// #define LEFT_ENCODER_SLIP_ADJUSTMENT 0.998733 // adjust this to make the robot go straight when it should
// #define RIGHT_ENCODER_SLIP_ADJUSTMENT 1.00127 // adjust this to make the robot go straight when it should
#endif


*/

#if defined(MOTHER_ROBOT) && defined(DAUGHTER_ROBOT) || !defined(MOTHER_ROBOT) && !defined(DAUGHTER_ROBOT)
#error "Only one robot can be defined: MOTHER_ROBOT or DAUGHTER_ROBOT"
#endif

#ifdef DAUGHTER_ROBOT
// TODO: MEASURE THESE VALUES FOR THE MOTHER ROBOT and calibrate the adjustments to make it go straight and turn the correct amount when it should
#define WHEEL_BASE 0.165
#define WHEEL_RADIUS 0.032
#define WHEEL_RADIUS_ADJUSTMENT 1.0 // this includes gear ration and encoder resolution
#define WHEEL_BASE_ADJUSTMENT 0.9568421053  // adjust this to make the robot turn the correct amount when it should
#define ADJUSTED_WHEEL_BASE (WHEEL_BASE * WHEEL_BASE_ADJUSTMENT)
#define GEAR_RATIO 46.67 // adjust this to make the robot go the correct distance when it should
#define ENCODER_RESOLUTION 8 // 8, 12 or 22 pulses check
#define STEPS_PER_REVOLUTION (GEAR_RATIO * ENCODER_RESOLUTION)
#define LEFT_ENCODER_SLIP_ADJUSTMENT 1.0 // adjust this to make the robot go straight when it should
#define RIGHT_ENCODER_SLIP_ADJUSTMENT 1.0 // adjust this to make the robot go straight when it should
#endif

#ifdef MOTHER_ROBOT
// TODO: MEASURE THESE VALUES FOR THE MOTHER ROBOT and calibrate the adjustments to make it go straight and turn the correct amount when it should
#define WHEEL_BASE 0.255
#define WHEEL_RADIUS 0.032
#define WHEEL_RADIUS_ADJUSTMENT 1.017 // this includes gear ration and encoder resolution
#define WHEEL_BASE_ADJUSTMENT 0.9863013699 // adjust this to make the robot turn the correct amount when it should
#define ADJUSTED_WHEEL_BASE (WHEEL_BASE * WHEEL_BASE_ADJUSTMENT)
#define GEAR_RATIO 46.67 // adjust this to make the robot go the correct distance when it should
#define ENCODER_RESOLUTION 8 // 8, 12 or 22 pulses check
#define STEPS_PER_REVOLUTION (GEAR_RATIO * ENCODER_RESOLUTION)
#define LEFT_ENCODER_SLIP_ADJUSTMENT 1.0 // adjust this to make the robot go straight when it should
#define RIGHT_ENCODER_SLIP_ADJUSTMENT 1.0 // adjust this to make the robot go straight when it should
#endif



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
    void moveDirection(float direction, uint8_t speed);
    void handleLeftEncoder();
    void handleRightEncoder();
    void setupEncoders();
    void updateLineFollow();
    void updateOdometry();
    float wrap_angle(float angle);
public:
    static MainDrive* singletonInstance;
    static void pulseCheckLeftEncoder();
    static void pulseCheckRightEncoder();
    static void targetReached(int16_t slot, int16_t exitId);
    
    float gyroZ = 0;
    float globalX_m = 0;
    float globalY_m = 0;
    float globalTheta_rad = 0;

    long lastLeftEncoderPos = 0;
    long lastRightEncoderPos = 0;

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
    void MoveSteps(int steps);
    void RotateSteps(int degrees);
    void SetVelocity(float vel, float omega);
};

#endif