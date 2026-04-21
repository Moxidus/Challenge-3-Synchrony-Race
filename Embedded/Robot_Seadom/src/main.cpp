#include "Libs/GripperLib.h"
#include <Arduino.h>
#include <Wire.h>
#include <ctype.h>
#include "MeMegaPi.h"
#include "Libs/MainDriveLib.h"
#include "Libs/LinearMotor.h"

struct WayPoint
{
  float x;     // Front is positive
  float y;     // Left is positive
  float theta; // Anti-cloways is positive
};

struct PalfaBeta
{
  float distance;
  float alfa;
  float beta;
};

#if defined(MOTHER_ROBOT) && defined(DAUGHTER_ROBOT)
#error "Only one robot can be defined: MOTHER_ROBOT or DAUGHTER_ROBOT"
#endif

#ifdef DAUGHTER_ROBOT
Gripper gripper(PORT4A);
MainDrive mainDrive(6, SLOT1, SLOT2);
MeGyro gyro(PORT7);
float KP = 0.05;
float KI = 0.001;
float KD = 0.3;
bool invertForward = false;
#endif

#ifdef MOTHER_ROBOT
Gripper gripper(PORT3A);
MainDrive mainDrive(6, SLOT2, SLOT4);
LinearMotor linearMotor(SLOT1);
MeGyro gyro(PORT6);
float KP = 0.3;
float KI = 0.000;
float KD = 0.2;
bool invertForward = false;
#endif

int executeCommand(String cmd);
void HandleCommands();
void setUpBluetooth();
void MoveToPointUpdate();
void startPointTracking(WayPoint targetPoint);

unsigned long timeSinceStart = 0;

void setup()
{
  Serial.begin(115200);

  setUpBluetooth();
  mainDrive.SetupLineFollow(KP, KI, KD, invertForward);
  mainDrive.StopFollowing();

// mother ship only setup
#ifdef MOTHER_ROBOT
  linearMotor.SetupLinearMotor();
#endif

// Daughter ship only setup
#ifdef DAUGHTER_ROBOT
#endif

  gyro.begin();

  timeSinceStart = millis();
}

void loop()
{

#ifdef DAUGHTER_ROBOT
#endif

  gyro.update();
  HandleCommands();

  mainDrive.gyroZ = gyro.getGyroZ(); // Gyro was causing problems so we are not using it at the moment
  mainDrive.UpdateMainDrive();
  gripper.update();
  MoveToPointUpdate();

#ifdef MOTHER_ROBOT
  linearMotor.Update();
#endif

  // testing remove after START --------------------------------------
  // static bool hasMoved = false;
  // static bool hasFliped = false;
  // if (!hasFliped && mainDrive.globalX > 5000) // move after 6 seconds for testing
  // {
  //   // test left wheel distance traveled
  //   // mainDrive.leftEncoder.move(-368);
  //   mainDrive.Flip();
  //   hasFliped = true;
  // }

  // if (hasFliped && mainDrive.globalX < 1000){
  //   // mainDrive.leftEncoder.move(-368);
  //   mainDrive.Flip();
  //   hasFliped = false;

  // }

  // if (!hasMoved && millis() - timeSinceStart > 6000) // move after 6 seconds for testing
  // {
  //   Serial.println("Moving forward");
  //   // mainDrive.leftEncoder.setTarPWM(100);
  //   mainDrive.leftEncoder.runSpeed(30);
  //   mainDrive.rightEncoder.runSpeed(30);

  //   hasMoved = true;
  // }

  // // if( millis() - timeSinceStart > 3000 && !hasMoved2) // move after 12 seconds for testing
  // // {
  // //   // test right wheel distance traveled
  // //   // mainDrive.rightEncoder.move(368);
  // //   mainDrive.RotateSteps(900);

  // //   hasMoved2 = true;
  // // }

  // if ( millis() % 5000 < 20 ) // print odometry every second
  // {
  // }

  // // print gyro stats
  // Serial.print("Gyro: ");
  // Serial.print(gyro.getGyroX());
  // Serial.print(",\t");
  // Serial.print(gyro.getGyroY());
  // Serial.print(",\t");
  // Serial.println(gyro.getGyroZ());

  // long deltaLeft = mainDrive.leftEncoder.getCurPos() - lastLeftEncoderPos;
  // we check the actually distance and measured distance and calibrate the radius adjustment

  // testing remove after END -----------------------------------------

  delay(1); // TODO: fix pid loop to not need this delay
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
  else if (cmd.startsWith("linmove "))
  {
    cmd.replace("linmove ", "");
    int val = cmd.toInt();
    linearMotor.move(val);
  }
#endif
  else if (cmd == "celebrate")
  {
    // TODO: Implement Celebration
  }
  else if (cmd.startsWith("start point"))
  {
    // The command is "start point x y thata"
    // Find the space after 'point'
    int space1 = cmd.indexOf(' ', 7); // Start search after "start "
    int space2 = cmd.indexOf(' ', space1 + 1);
    int space3 = cmd.indexOf(' ', space2 + 1);

    Serial.println("Received start point command: " + cmd.substring(space2 + 1, space3) + " " + cmd.substring(space3 + 1) + " " + cmd.substring(space1 + 1, space2));

    if (space1 != -1 && space2 != -1 && space3 != -1)
    {
      float x = cmd.substring(space1 + 1, space2).toFloat();
      float y = cmd.substring(space2 + 1, space3).toFloat();
      float theta = cmd.substring(space3 + 1).toFloat();
      theta = theta * DEG_TO_RAD;

      Serial.print("Start Point Set: ");
      Serial.print(x);
      Serial.print(", ");
      Serial.print(y);
      Serial.print(", ");
      Serial.println(theta);

      // Now you can use x, y, and theta to set the starting point for your navigation

      startPointTracking({x, y, theta});
    }
  }
  else if (cmd.startsWith("start relpoint"))
  {
    // The command is "start point x y thata"
    // Find the space after 'point'
    int space1 = cmd.indexOf(' ', 7); // Start search after "start "
    int space2 = cmd.indexOf(' ', space1 + 1);
    int space3 = cmd.indexOf(' ', space2 + 1);

    Serial.println("Received start relative point command: " + cmd.substring(space2 + 1, space3) + " " + cmd.substring(space3 + 1) + " " + cmd.substring(space1 + 1, space2));

    if (space1 != -1 && space2 != -1 && space3 != -1)
    {
      float x = cmd.substring(space1 + 1, space2).toFloat();
      float y = cmd.substring(space2 + 1, space3).toFloat();
      float theta = cmd.substring(space3 + 1).toFloat();
      theta = theta * DEG_TO_RAD;

      Serial.print("relative Point Set: ");
      Serial.print(x);
      Serial.print(", ");
      Serial.print(y);
      Serial.print(", ");
      Serial.println(theta);

      // rotate
      // TODO: MAKE SURE THE ROTATION IS IN THE CORRECT DIRRECTION
      float rotatedX = cos(theta) * x + -sin(theta) * y;
      float rotatedY = sin(theta) * x + cos(theta) * y;

      // Now you can use x, y, and theta to set the starting point for your navigation
      startPointTracking({rotatedX + mainDrive.globalX_m, rotatedY + mainDrive.globalY_m, theta + mainDrive.globalTheta_rad});

      // Example: myNavigator.SetStart(x, y, z);
    }
  }
  else if (cmd == "stop point")
  {
    // TODO: Implement
  }
  else if (cmd.startsWith("vel"))
  {
    // Find the first space (after "vel")
    int firstSpace = cmd.indexOf(' ');
    // Find the second space (between v and omega)
    int secondSpace = cmd.indexOf(' ', firstSpace + 1);

    if (firstSpace != -1 && secondSpace != -1)
    {
      float v = cmd.substring(firstSpace + 1, secondSpace).toFloat();
      float omega = cmd.substring(secondSpace + 1).toFloat();
      mainDrive.SetVelocity(v, omega);
    }
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
  else if (cmd.startsWith("getencoders"))
  {
    Serial3.print("Left Encoder: ");
    Serial3.print(mainDrive.leftEncoder.getCurPos());
    Serial3.print(" Right Encoder: ");
    Serial3.println(mainDrive.rightEncoder.getCurPos());
  }
  else if (cmd.startsWith("getpos"))
  {
    Serial3.print("X: ");
    Serial3.print(mainDrive.globalX_m);
    Serial3.print(" Y: ");
    Serial3.print(mainDrive.globalY_m);
    Serial3.print(" Theta: ");
    Serial3.println(mainDrive.globalTheta_rad * RAD_TO_DEG); // Thetat gets outputed to degrees
  }
  else if (cmd.startsWith("resetpos"))
  {
    mainDrive.globalX_m = 0;
    mainDrive.globalY_m = 0;
    mainDrive.globalTheta_rad = 0;
  }
  else
  {
    Serial.println("Unknown command: " + cmd);
    Serial3.println("Unknown command: " + cmd);
  }

  Serial.println("executed command: " + cmd);

  return 0;
}






#define kp (0.005)
#define kAlfa (5.5)
#define kBeta (-3.80)


// #define kp (0.005)
// #define kAlfa (8.5)
// #define kBeta (-0.12)


// #define kBeta_x (-15.5 / 10)

#define vMax 1.0     // m/s
#define omegaMax 1.0 // rad/s

bool isTrackingPoint = false;
WayPoint TargetPoint;

void startPointTracking(WayPoint targetPoint)
{

  TargetPoint = targetPoint;
  Serial.println("Target Pose: (" + String(TargetPoint.x) + ", " + String(TargetPoint.y) + ", " + String(TargetPoint.theta) + ")");
  isTrackingPoint = true;
}

float deg2rad(float deg)
{
  return deg * (PI / 180.0);
}

WayPoint getError(WayPoint currentPose, WayPoint targetPose)
{

  // Translation: target relative to robot
  float dx = targetPose.x - currentPose.x;
  float dy = targetPose.y - currentPose.y;

  float theta = currentPose.theta;

  // Rotation into robot frame
  float dx_r = cos(theta) * dx + sin(theta) * dy;
  float dy_r = -sin(theta) * dx + cos(theta) * dy;

  // Orientation error
  float dtheta = targetPose.theta - currentPose.theta;
  dtheta = atan2(sin(dtheta), cos(dtheta));

  WayPoint errorCoords = {dx_r, dy_r, dtheta};

  return errorCoords;
}

PalfaBeta getPAlfaBeta(WayPoint errorCoords)
{
  float distance = sqrt(errorCoords.x * errorCoords.x + errorCoords.y * errorCoords.y);

  float alfa = atan2(errorCoords.y, errorCoords.x);
  alfa = atan2(sin(alfa), cos(alfa)); // Normalize to [-pi, pi]

  float beta = errorCoords.theta - alfa;
  beta = atan2(sin(beta), cos(beta)); // Normalize to [-pi, pi]

  PalfaBeta pAlfaBeta = {distance, alfa, beta};
  return pAlfaBeta;
}

float getVelocity(PalfaBeta pAlfaBeta)
{
  return kp * pAlfaBeta.distance;
}

float getAngularVelocity(PalfaBeta pAlfaBeta)
{
  return kAlfa * pAlfaBeta.alfa + kBeta * pAlfaBeta.beta;
}

void MoveToPointUpdate()
{
  if (!isTrackingPoint)
    return;

  WayPoint currentPos = {mainDrive.globalX_m, mainDrive.globalY_m, mainDrive.globalTheta_rad};
  WayPoint errorCoords = getError(currentPos, TargetPoint);
  PalfaBeta pAlfaBeta = getPAlfaBeta(errorCoords);

  // --- Thresholds (tune these) ---
  const float distThresh = 0.04f; // m
  const float thetaThresh = 10.0f * DEG_TO_RAD;
  const float alfaDeadzone = 0.04f; // m — stop steering by alfa when this close

  Serial.print(" error x: ");
  Serial.print(errorCoords.x);
  Serial.print(", error y: ");
  Serial.print(errorCoords.y);
  Serial.print(", error theta: ");
  Serial.print(errorCoords.theta * RAD_TO_DEG);
  Serial.print(", error abs theta: ");
  Serial.println(fabs(errorCoords.theta) * RAD_TO_DEG);
  // Serial.print(omega);

  Serial.print(" current x: ");
  Serial.print(currentPos.x);
  Serial.print(",  current y: ");
  Serial.print(currentPos.y);
  Serial.print(",  current theta: ");
  Serial.println(currentPos.theta * RAD_TO_DEG);
  
  Serial.print(" beta: ");
  Serial.print(pAlfaBeta.beta);
  Serial.print(", dist: ");
  Serial.print(pAlfaBeta.distance);
  Serial.print(", alfa: ");
  Serial.println(pAlfaBeta.alfa);

  if (pAlfaBeta.distance < distThresh && fabs(errorCoords.theta) < thetaThresh)
  {
    Serial.println("Reached waypoint, stopping");
    mainDrive.StopFollowing();
    mainDrive.SetVelocity(0, 0);
    isTrackingPoint = false;
    return;
  }

  float vel = getVelocity(pAlfaBeta);
  float omega = getAngularVelocity(pAlfaBeta);

  // Kill alfa steering when very close — only correct final heading
  // if (pAlfaBeta.distance < alfaDeadzone)
  // {
  //   omega = -kBeta * errorCoords.theta;
  // }

  vel = constrain(vel, -vMax, vMax) * max(0.0f, cos(pAlfaBeta.alfa));
  omega = constrain(omega, -omegaMax, omegaMax);

  Serial.print("vel: ");
  Serial.print(vel);
  Serial.print(", omega: ");
  Serial.println(omega);

  mainDrive.SetVelocity(vel * 1000.0f, omega);
}