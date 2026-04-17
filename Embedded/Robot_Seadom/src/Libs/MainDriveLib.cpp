#include "MainDriveLib.h"
#include <Arduino.h>
#include "MeMegaPi.h"


MainDrive* MainDrive::singletonInstance = nullptr;

MainDrive::MainDrive(uint8_t lineSensorPort, uint8_t leftEncoderPort, uint8_t rightEncoderPort)
    : leftEncoder(leftEncoderPort),
      rightEncoder(rightEncoderPort),
      lineFollowerSensor(lineSensorPort){
        
}


void MainDrive::SetupLineFollow(float kp, float ki, float kd, bool inverForward){

    setupEncoders();

    this->kp = kp;
    this->ki = ki;
    this->kd = kd;
    this->invertForward = inverForward;


    i = 0;
    d = 0;
    lastE = 0;

    softStartTimer = millis();
    Serial.println("Line following started");
}


void MainDrive::UpdateMainDrive(float gyroZ){

    leftEncoder.loop();
    rightEncoder.loop();

    updateOdometry(gyroZ);
    
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

    
    moveDirection(pid, defaultSpeed);

}


void MainDrive::StopFollowing(){
    isStopped = true;
    
    i = 0;
    d = 0;
    lastE = 0;

    leftEncoder.setMotorPwm(0);
    rightEncoder.setMotorPwm(0);
}

void MainDrive::ResumeFollowing(){
    isStopped = false;
    leftEncoder.setMotionMode(PWM_MODE);
    rightEncoder.setMotionMode(PWM_MODE);
    moveDirection(0, defaultSpeed);
}

void MainDrive::SetDefaultSpeed(int newSpeed){
    newSpeed = constrain(newSpeed, 0, MAX_SPEED);
    defaultSpeed = newSpeed;
}



void MainDrive::MoveSteps(int steps){
    bool lastIsStoped = isStopped;
    StopFollowing();

    delay(300); // wait for motors to stop

    // pure 180 is about 475 not 530
    // overshoot 180 by about 10 degrees
    leftEncoder.setMotorPwm(0);
    rightEncoder.setMotorPwm(0);
    if(invertForward){
        leftEncoder.move(steps, ((float)defaultSpeed/MAX_SPEED)*100);
        rightEncoder.move(-steps, ((float)defaultSpeed/MAX_SPEED)*100);
    }else{
        leftEncoder.move(-steps, ((float)defaultSpeed/MAX_SPEED)*100);
        rightEncoder.move(steps, ((float)defaultSpeed/MAX_SPEED)*100);
    }

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


void MainDrive::RotateSteps(int degrees){
    bool lastIsStoped = isStopped;
    StopFollowing();

    leftEncoder.setMotorPwm(0);
    rightEncoder.setMotorPwm(0);
    leftEncoder.setTarPWM(0);
    rightEncoder.setTarPWM(0);
    leftEncoder.loop();
    rightEncoder.loop();
    delay(300); // wait for motors to stop

    // pure 180 is about 475 not 530
    // overshoot 180 by about 10 degrees
    leftEncoder.setMotorPwm(0);
    rightEncoder.setMotorPwm(0);

    // conver degrees to steps
    int steps = (int)((degrees/360.0) * (PI * ADJUSTED_WHEEL_BASE) / (2 * PI * WHEEL_RADIUS) * STEPS_PER_REVOLUTION); // 8 pulses per revolution and 46.67 gear ratio

    if(invertForward){
        leftEncoder.move(-steps, ((float)defaultSpeed/MAX_SPEED)*100);
        rightEncoder.move(-steps, ((float)defaultSpeed/MAX_SPEED)*100);
    }else{
        leftEncoder.move(steps, ((float)defaultSpeed/MAX_SPEED)*100);
        rightEncoder.move(steps, ((float)defaultSpeed/MAX_SPEED)*100);
    }

    // wait until we reach the target
    while (!(leftEncoder.isTarPosReached() && rightEncoder.isTarPosReached()))
    {
        UpdateMainDrive(0.0f); // updates positions
        getAndUpdatePos(); // makes sure the robot knows where the line is
    }

    // Turn off PID mode
    leftEncoder.setMotionMode(PWM_MODE);
    rightEncoder.setMotionMode(PWM_MODE);
    

    // resume line
    if (!lastIsStoped)
        ResumeFollowing();
}

void MainDrive::SetVelocity(float vel, float omega)
{
    // disable line following when using this function as it is used for manual control and line following would interfere with that, we can add a flag later to allow line following and velocity control at the same time but for now we will just disable line following when using this function
    if (!isStopped)
        StopFollowing();

    // calulate left and right wheel speeds based on desired velocity and angular velocity, we will need to scale these values based on the max speed of the robot and the desired velocity and angular velocity
    // we will also need to convert these values to PWM values between -255 and 255
    float leftWheelV = vel - (omega/ (ADJUSTED_WHEEL_BASE* 2))*1000;
    float rightWheelV = vel + (omega/ (ADJUSTED_WHEEL_BASE* 2))*1000;
    leftWheelV = leftWheelV / WHEEL_RADIUS;
    rightWheelV = rightWheelV / WHEEL_RADIUS;

    // TODO: constrain to max values

    float leftWheelPWM = (leftWheelV / MAX_SPEED) * defaultSpeed;
    float rightWheelPWM = (rightWheelV / MAX_SPEED) * defaultSpeed;

    Serial.println("Left wheel velocity: " + String(leftWheelV) + " Right wheel velocity: " + String(rightWheelV));


    if(invertForward){
        leftEncoder.setTarPWM(leftWheelPWM);
        rightEncoder.setTarPWM(-rightWheelPWM);
    }
    else{
        leftEncoder.setTarPWM(-leftWheelPWM);
        rightEncoder.setTarPWM(rightWheelPWM);
    }


}

// Function to move the robot in a certain direction with a given speed (-1.0 for full left, 1.0 for full right, 0 for straight)
void MainDrive::moveDirection(float direction, uint8_t speed){


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

    Serial.println("Direction: " + String(direction) + " Speed: " + String(speed) + " Left PWM: " + String(leftPWM) + " Right PWM: " + String(rightPWM));

    if(invertForward){
        leftEncoder.setMotorPwm(leftPWM);
        rightEncoder.setMotorPwm(-rightPWM);
    }else{
        leftEncoder.setMotorPwm(-leftPWM);
        rightEncoder.setMotorPwm(rightPWM);
    }




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
    if(invertForward){
        leftEncoder.move(-530, 100, 1, targetReached);
        rightEncoder.move(-530, 100, 2, targetReached);
    }else{
        leftEncoder.move(530, 100, 1, targetReached);
        rightEncoder.move(530, 100, 2, targetReached);
    }

    // wait until we reach the target
    while (!(leftEncoder.isTarPosReached() && rightEncoder.isTarPosReached()))
    {
        UpdateMainDrive(0.0f); // updates positions
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
    leftEncoder.setPosPid(1.8,0,1.2);   // Position PID gains (P, I, D) these values have been obtained from the generated mblock code
    leftEncoder.setSpeedPid(0.18,0,0);

    rightEncoder.setPulse(8);            // Encoder pulses per motor revolution (hardware-specific)
    rightEncoder.setRatio(46.67);        // Gear ratio used for position/speed calculations
    rightEncoder.setPosPid(1.8,0,1.2);   // Position PID gains (P, I, D) these values have been obtained from the generated mblock code
    rightEncoder.setSpeedPid(0.18,0,0); 

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
void MainDrive::updateOdometry(float gyroZ)
{
    noInterrupts(); // Ensure atomic access to encoder counts
    long rawLeft  = leftEncoder.getCurPos();
    long rawRight = rightEncoder.getCurPos();
    interrupts(); // Re-enable interrupts

    // Adjust signs so that forward motion gives positive delta on both wheels
    // Verify: drive forward manually, confirm both deltas positive
    long deltaLeft  = (invertForward ?  rawLeft : -rawLeft) - lastLeftEncoderPos;
    long deltaRight = (invertForward ? -rawRight : rawRight) - lastRightEncoderPos;

    // TODO: TEST IF IT ACTUALLY WORKS
     // Only update when we have enough ticks to be meaningful
    if (abs(deltaLeft) + abs(deltaRight) < 4)
        return;

    static unsigned long lastOdTime = micros();
    unsigned long now = micros();
    float dt = (now - lastOdTime) / 1e6f;
    lastOdTime = now;

    lastLeftEncoderPos  = (invertForward ?  rawLeft : -rawLeft);
    lastRightEncoderPos = (invertForward ? -rawRight : rawRight);

    // Use a SINGLE shared slip/scale constant until properly calibrated
    // Asymmetric constants bake a permanent curve into straight lines
    float d_l = (deltaLeft  / STEPS_PER_REVOLUTION) * 2 * PI * WHEEL_RADIUS * WHEEL_RADIUS_ADJUSTMENT;
    float d_r = (deltaRight / STEPS_PER_REVOLUTION) * 2 * PI * WHEEL_RADIUS * WHEEL_RADIUS_ADJUSTMENT;

    float v         = (d_l + d_r) * 0.5f;
    float dtheta    = (d_r - d_l) / ADJUSTED_WHEEL_BASE;

    if (abs(dtheta) < 1e-4f)  // straight line — arc formula unstable here
    {
        globalX += v * cos(globalTheta);
        globalY += v * sin(globalTheta);
    }
    else
    {
        float R    = v / dtheta;
        float midTheta = globalTheta + dtheta * 0.5f; // midpoint integration (more accurate)
        globalX += R * (sin(globalTheta + dtheta) - sin(globalTheta));
        globalY += R * (cos(globalTheta) - cos(globalTheta + dtheta));
    }

    globalTheta = wrap_angle(globalTheta + dtheta);
}

// wrap angle to [-pi, pi]
float MainDrive::wrap_angle(float angle)
{
  while (angle > PI)
    angle -= 2 * PI;
  while (angle < -PI)
    angle += 2 * PI;
  return angle;
}