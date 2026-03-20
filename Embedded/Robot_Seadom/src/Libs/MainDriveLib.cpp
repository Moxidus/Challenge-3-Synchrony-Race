#include "MainDriveLib.h"
#include <Arduino.h>
#include "MeMegaPi.h"

MainDrive* MainDrive::singletonInstance = nullptr;

MainDrive::MainDrive(uint8_t lineSensorPort, uint8_t leftEncoderPort, uint8_t rightEncoderPort)
    : leftEncoder(leftEncoderPort),
      rightEncoder(rightEncoderPort),
      lineFollowerSensor(lineSensorPort){
        
}


void MainDrive::SetupLineFollow(float kp, float ki, float kd){

    setupEncoders();

    this->kp = kp;
    this->ki = ki;
    this->kd = kd;


    i = 0;
    d = 0;
    lastE = 0;

    softStartTimer = millis();
    Serial.println("Line following started");
}


void MainDrive::UpdateMainDrive(){

    leftEncoder.loop();
    rightEncoder.loop();

    if (isStopped) // stops following if 
        return;

    updateLineFollow();
}

void MainDrive::updateLineFollow(){    

    int pos = getAndUpdatePos();
    int e = pos - setPoint;

    float p = kp*e;

    i += e*ki;
    i = constrain(i, -1.0, 1.0);

    d += (e - lastE)*kd;
    lastE = e;

    // impulse decay for the D term
    if ( d > 0){ // decay rate
        d -= 0.001;
    }if ( d < 0){ // decay rate
        d += 0.001;
    }   
       
    
    float pid = p + i + d;

    // Serial.println("P: " + String(p));
    // Serial.println("I: " + String(i));
    // Serial.println("D: " + String(d));
    // Serial.println("pos L: " + String(leftEncoder.getCurPos()));
    
    pid = constrain(pid, -1.0, 1.0);

    
    moveDirection(pid);

}


void MainDrive::StopFollowing(){
    isStopped = true;
    
    i = 0;
    d = 0;
    lastE = 0;

    moveDirection(0,0);
}

void MainDrive::ResumeFollowing(){
    isStopped = false;
    moveDirection(0);
}

void MainDrive::SetDefaultSpeed(uint8_t newSpeed){
    defaultSpeed = newSpeed;
}


// Function to move the robot in a certain direction with a given speed (-1.0 for full left, 1.0 for full right, 0 for straight)
void MainDrive::moveDirection(float direction, uint8_t speed){

    if(speed == NULL)
        speed = defaultSpeed;

    if (softStartTimer + softStartDuration > millis()) {
        // During the soft start period, scale the speed based on elapsed time
        float scale = (float)(millis() - softStartTimer) / softStartDuration;
        speed = (int)(speed * scale);
    }

    speed = constrain(speed, 0, MAX_SPEED);

    int leftPWM = speed;
    int rightPWM = speed;

    if (direction < 0.0) {
        rightPWM -= (int)(-direction * speed);  // Reduce right motor PWM for left turns
    } else if (direction > 0.0) {
        leftPWM -= (int)(direction * speed);    // Reduce left motor PWM for right turns
    }

    // Motor PWM values should be between -255 and 255
    leftPWM = constrain(leftPWM, 0, MAX_SPEED);
    rightPWM = constrain(rightPWM, 0, MAX_SPEED);

    leftEncoder.setMotorPwm(-leftPWM);
    rightEncoder.setMotorPwm(rightPWM);
    // later we should move to setTarPWM as it handles acceleration better but it breaks line tracking so for now we will use setMotorPWM
    // leftEncoder.setTarPWM
}

int MainDrive::getAndUpdatePos(){
    static int lastDirection = 1; // 1 left, 5 right

    int s1 = lineFollowerSensor.readSensor1();
    int s2 = lineFollowerSensor.readSensor2();

    if (s1 == 0 && s2 == 0) {
        return 3;
    } else if (s1 == 0 && s2 == 1) {
        lastDirection = 1;
        return 2;
    } else if (s1 == 1 && s2 == 0) {
        lastDirection = 5;
        return 4;
    } else {
        return lastDirection;
    }
}


// motion control


// TODO: Implement line search function so that it automatically finds in which dirrection is the line
void MainDrive::Flip(){
    bool lastIsStoped = isStopped;
    StopFollowing();

    delay(300); // wait for motors to stop

    // pure 180 is about 475 not 530
    // overshoot 180 by about 10 degrees
    leftEncoder.move(530, 100, 1, targetReached);
    rightEncoder.move(530, 100, 2, targetReached);

    // wait until we reach the target
    while (!(leftEncoder.isTarPosReached() && rightEncoder.isTarPosReached()))
    {
        UpdateMainDrive(); // updates positions
        getAndUpdatePos(); // makes sure the robot knows where the line is
    }

    // Turn off PID mode
    leftEncoder.setMotionMode(PWM_MODE);
    rightEncoder.setMotionMode(PWM_MODE);
    

    // resume line
    if (!lastIsStoped)
        ResumeFollowing();
}


void MainDrive::targetReached(int16_t slot, int16_t exitId){
    // Serial.println("Target at " + String(slot) + "was reached with id " + String(exitId));
    // might be usefull in the future
}


// Encoder setup

void MainDrive::setupEncoders(){
    Serial.println("Encoder setup");

    singletonInstance = this;

    attachInterrupt(leftEncoder.getIntNum(), pulseCheckLeftEncoder, RISING);  // Count pulses on rising edges
    attachInterrupt(rightEncoder.getIntNum(), pulseCheckRightEncoder, RISING);  // Count pulses on rising edges

    //TODO: Tune the PID values for the motors 

    leftEncoder.setPulse(8);            // Encoder pulses per motor revolution (hardware-specific)
    leftEncoder.setRatio(46.67);        // Gear ratio used for position/speed calculations
    leftEncoder.setSpeedPid(0.18,0,0);
    leftEncoder.setPosPid(1.8,0,1.2);   // Position PID gains (P, I, D) these values have been obtained from the generated mblock code

    rightEncoder.setPulse(8);            // Encoder pulses per motor revolution (hardware-specific)
    rightEncoder.setRatio(46.67);        // Gear ratio used for position/speed calculations
    rightEncoder.setSpeedPid(0.18,0,0); 
    rightEncoder.setPosPid(1.8,0,1.2);   // Position PID gains (P, I, D) these values have been obtained from the generated mblock code

}


void MainDrive::pulseCheckLeftEncoder() {
    singletonInstance->handleLeftEncoder();
}

void MainDrive::pulseCheckRightEncoder() {
    singletonInstance->handleRightEncoder();
}

void MainDrive::handleLeftEncoder(void)
{
    // Interrupt handler for left encoder pulse counting.
    if (digitalRead(leftEncoder.getPortB()) == 0)
    {
        leftEncoder.pulsePosMinus(); 
    }
    else
    {
        leftEncoder.pulsePosPlus();  
    }
}

void MainDrive::handleRightEncoder(void)
{
    // Interrupt handler for right encoder pulse counting.
    if (digitalRead(rightEncoder.getPortB()) == 0)
    {
        rightEncoder.pulsePosMinus(); 
    }
    else
    {
        rightEncoder.pulsePosPlus();  
    }
}

