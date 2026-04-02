#include "Libs/GripperLib.h"
#include <Arduino.h>
#include <Wire.h>
#include <ctype.h>
#include "MeMegaPi.h"
#include "Libs/MainDriveLib.h"
#include "Libs/LinearMotor.h"

// SELECT ROBOT YOU ARE PROGRAMMING!!!
// #define MOTHER_ROBOT
#define DAUGHTER_ROBOT

#if defined(MOTHER_ROBOT) && defined(DAUGHTER_ROBOT)
#error "Only one robot can be defined: MOTHER_ROBOT or DAUGHTER_ROBOT"
#endif

#ifdef DAUGHTER_ROBOT
Gripper gripper(PORT4A);
MainDrive mainDrive(6, SLOT1, SLOT2);
float KP = 0.05;
float KI = 0.001;
float KD = 0.3;
bool invertForward = false;
// TODO: MEASURE THESE VALUES FOR THE MOTHER ROBOT and calibrate the adjustments to make it go straight and turn the correct amount when it should
#define WHEEL_BASE 165
#define WHEEL_RADIUS 32
#define WHEEL_RADIUS_ADJUSTMENT 1.0 // adjust this to make the robot go straight when it should
#define WHEEL_BASE_ADJUSTMENT 1.0 // adjust this to make the robot turn the correct amount when it should
#endif

#ifdef MOTHER_ROBOT
Gripper gripper(PORT3A);
MainDrive mainDrive(6, SLOT2, SLOT1);
LinearMotor linearMotor(SLOT4);
float KP = 0.3;
float KI = 0.000;
float KD = 0.2;
bool invertForward = true;
// TODO: MEASURE THESE VALUES FOR THE MOTHER ROBOT and calibrate the adjustments to make it go straight and turn the correct amount when it should
#define WHEEL_BASE 165
#define WHEEL_RADIUS 32
#define WHEEL_RADIUS_ADJUSTMENT 1.0 // adjust this to make the robot go straight when it should
#define WHEEL_BASE_ADJUSTMENT 1.0 // adjust this to make the robot turn the correct amount when it should
#endif

int executeCommand(String cmd);
void HandleCommands();
void setUpBluetooth();
float wrap_angle(float angle);
void updateOdometry();

// Global frame
float globalX = 0;
float globalY = 0;
float globalTheta = 0;

long lastLeftEncoderPos = 0;
long lastRightEncoderPos = 0;

void setup()
{
  Serial.begin(115200);

  setUpBluetooth();
  mainDrive.SetupLineFollow(KP, KI, KD, invertForward);
  mainDrive.StopFollowing();

#ifdef MOTHER_ROBOT
  linearMotor.SetupLinearMotor();
#endif
}

void loop()
{
  HandleCommands();

  mainDrive.UpdateMainDrive();
  gripper.update();

#ifdef MOTHER_ROBOT
  linearMotor.Update();
#endif

  updateOdometry();

  delay(1); // TODO: fix pid loop to not need this delay
}

void updateOdometry()
{
  // get the distance traveled by each wheel since last update
  long deltaLeft = mainDrive.leftEncoder.getCurPos() - lastLeftEncoderPos;
  long deltaRight = mainDrive.rightEncoder.getCurPos() - lastRightEncoderPos;

  lastLeftEncoderPos = mainDrive.leftEncoder.getCurPos();
  lastRightEncoderPos = mainDrive.rightEncoder.getCurPos();

  float d_l_meas = deltaLeft * WHEEL_RADIUS * WHEEL_RADIUS_ADJUSTMENT;
  float d_r_meas = deltaRight * WHEEL_RADIUS * WHEEL_RADIUS_ADJUSTMENT;

  float v = 0.5 * (d_l_meas + d_r_meas);
  float omega = (d_r_meas - d_l_meas) / (WHEEL_BASE * WHEEL_BASE_ADJUSTMENT);

  if (abs(omega) < 1e-6) // straight line approximation
  {
    globalX += v * cos(globalTheta);
    globalY += v * sin(globalTheta);
  }
  else
  {
    float R = v / omega;
    float relX = R * sin(omega);
    float relY = R * (1 - cos(omega));

    // rotate to global frame
    globalX += relX * cos(globalTheta) - relY * sin(globalTheta);
    globalY += relY * cos(globalTheta) + relX * sin(globalTheta);
  }

  globalTheta = wrap_angle(globalTheta + omega);
}

// wrap angle to [-pi, pi]
float wrap_angle(float angle)
{
  while (angle > PI)
    angle -= 2 * PI;
  while (angle < -PI)
    angle += 2 * PI;
  return angle;
}

void setUpBluetooth()
{
  Serial3.begin(115200);
  Serial.println("Bluetooth Start!");
}

void HandleCommands()
{
  static String command = "";

  while (Serial3.available())
  {
    char c = Serial3.read();

    if (c == '\n')
    {
      Serial.println("Command: " + command);
      executeCommand(command);
      command = "";
    }
    else
    {
      command += c;
    }
  }
}

int executeCommand(String cmd)
{
  if (cmd == "close grip")
  {
    gripper.close();
  }
  else if (cmd == "open grip")
  {
    gripper.open();
  }
  else if (cmd == "stop track")
  {
    mainDrive.StopFollowing();
  }
  else if (cmd == "start track")
  {
    mainDrive.ResumeFollowing();
  }
  else if (cmd == "flip")
  {
    mainDrive.Flip();
  }
#ifdef MOTHER_ROBOT // mother ship only commands

  else if (cmd == "lin home")
  {
    linearMotor.MoveHome();
  }
  else if (cmd == "lin down")
  {
    linearMotor.MoveDown();
  }
#endif
  else if (cmd == "celebrate")
  {
    // TODO: Implement Celebration
  }
  else if (cmd == "start point")
  {
    // TODO: Implement
  }
  else if (cmd == "stop point")
  {
    // TODO: Implement
  }
  else if (cmd.startsWith("point"))
  {
    int x, y;
    sscanf(cmd.c_str(), "point %d %d", &x, &y);
    // int val = cmd.toInt();
    Serial.println("moving to points: " + String(x) + " " + String(y));
  }
  else if (cmd.startsWith("move"))
  {
    cmd.replace("move", "");
    int val = cmd.toInt();
    mainDrive.MoveSteps(val);
  }
  else if (cmd.startsWith("rotate"))
  {
    cmd.replace("rotate", "");
    int val = cmd.toInt();
    mainDrive.RotateSteps(val);
  }
  else if (cmd.startsWith("setspeed"))
  {
    cmd.replace("setspeed", "");
    int val = cmd.toInt();
    mainDrive.SetDefaultSpeed(val);
  }
  else
  {
    Serial.println("Unknown command: " + cmd);
    Serial3.println("Unknown command: " + cmd);
  }

  Serial.println("executed command: " + cmd);

  return 0;
}