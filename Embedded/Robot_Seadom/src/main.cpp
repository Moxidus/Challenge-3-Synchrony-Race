#include "Libs/GripperLib.h"
#include <Arduino.h>
#include <Wire.h>
#include <ctype.h>
#include "MeMegaPi.h"
#include "Libs/MainDriveLib.h"
#include "Libs/LinearMotor.h"


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
#endif

#ifdef MOTHER_ROBOT
Gripper gripper(PORT3A);
MainDrive mainDrive(6, SLOT2, SLOT1);
LinearMotor linearMotor(SLOT4);
float KP = 0.3;
float KI = 0.000;
float KD = 0.2;
bool invertForward = true;
#endif

int executeCommand(String cmd);
void HandleCommands();
void setUpBluetooth();


unsigned long timeSinceStart = 0;

void setup()
{
  Serial.begin(115200);

  setUpBluetooth();
  mainDrive.SetupLineFollow(KP, KI, KD, invertForward);
  mainDrive.StopFollowing();

#ifdef MOTHER_ROBOT
  linearMotor.SetupLinearMotor();
#endif

  timeSinceStart = millis();


}


void loop()
{
  HandleCommands();

  mainDrive.UpdateMainDrive();
  gripper.update();

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
  //   // test left wheel distance traveled
  //   // mainDrive.leftEncoder.move(-368);
  //   // mainDrive.RotateSteps(475*10);
  //   mainDrive.ResumeFollowing();

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
  //   Serial3.print("X: ");
  //   Serial3.print(mainDrive.globalX);
  //   Serial3.print(" Y: ");
  //   Serial3.print(mainDrive.globalY);
  //   Serial3.print(" Theta: ");
  //   Serial3.println(mainDrive.globalTheta);
    
  //   //Serial.println("left encoder: " + String(mainDrive.leftEncoder.getCurPos()) + " right encoder: " + String(mainDrive.rightEncoder.getCurPos()));
  // }

  


  
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
    Serial3.print(mainDrive.globalX);
    Serial3.print(" Y: ");
    Serial3.print(mainDrive.globalY);
    Serial3.print(" Theta: ");
    Serial3.println(mainDrive.globalTheta);
  }
  else
  {
    Serial.println("Unknown command: " + cmd);
    Serial3.println("Unknown command: " + cmd);
  }

  Serial.println("executed command: " + cmd);

  return 0;
}



/*

    errorCoords = getError(robotInertialCoordinace, wayPoints[targetWayPointIndex])
   
    pAlfaBeta = getPAlfaBeta(errorCoords)

    # print error with 2 decimal places
    print(f"Error Coords: deltaX: {errorCoords[0]:.2f}, deltaY: {errorCoords[1]:.2f}, deltaTheta: {np.rad2deg(errorCoords[2]):.2f}deg", end=' | ')
    # print pAlfaBeta with 2 decimal places
    print(f"distance: {pAlfaBeta[0]:.2f}, alfa: {np.rad2deg(pAlfaBeta[1]):.2f}deg, beta: {np.rad2deg(pAlfaBeta[2]):.2f}deg" )



    if pAlfaBeta[0] < 1.0 and abs(errorCoords[2]) < np.deg2rad(5):
        targetWayPointIndex = (targetWayPointIndex + 1) % len(wayPoints)
        waypointQuivers[targetWayPointIndex-1].set_color('green')
        waypointQuivers[targetWayPointIndex].set_color('red')
        print("Reached waypoint, moving to next:", targetWayPointIndex)
        errorCoords = getError(robotInertialCoordinace, wayPoints[targetWayPointIndex])
        pAlfaBeta = getPAlfaBeta(errorCoords)

    # print float with 2 decimal places
    print(f"deltaX: {errorCoords[0]:.2f}, deltaY: {errorCoords[1]:.2f}, deltaTheta: {np.rad2deg(errorCoords[2]):.2f} deg", f"distance: {pAlfaBeta[0]:.2f}, alfa: {np.rad2deg(pAlfaBeta[1]):.2f} deg, beta: {np.rad2deg(pAlfaBeta[2]):.2f} deg" )
    

    vel = getVelocity(pAlfaBeta)
    omega = getAngularVelocity(pAlfaBeta)

    
    vel = np.clip(vel, -vMax, vMax) * max(0, np.cos(pAlfaBeta[1]))  # Reduce velocity when not facing the target
    omega = np.clip(omega, -omegaMax, omegaMax)


    robotInertialCoordinace[0] += np.cos(robotInertialCoordinace[2])*vel
    robotInertialCoordinace[1] += np.sin(robotInertialCoordinace[2])*vel
    robotInertialCoordinace[2] += omega
    robotInertialCoordinace[2] = np.arctan2(np.sin(robotInertialCoordinace[2]), np.cos(robotInertialCoordinace[2])) # Normalize angle to [-pi, pi]



*/

#define kp (3.0 / 10)
#define kAlfa (10.0 / 10)
#define kBeta (-1.5 / 10)

#define vMax 1.5 // m/s
#define omegaMax 0.1 // rad/s


struct WayPoint {
  float x;
  float y;
  float theta;
};

struct PalfaBeta {
  float distance;
  float alfa;
  float beta;
};



bool isTrackingPoint = false;

void startPointTracking(WayPoint targetPoint)
{
  isTrackingPoint = true;
}


float deg2rad(float deg) {
    return deg * (PI / 180.0);
}

WayPoint getError(WayPoint currentPose, WayPoint targetPose)
{
    // Translation: target relative to robot
    float dx = targetPose.x - currentPose.x;
    float dy = targetPose.y - currentPose.y;

    float theta = currentPose.theta;

    // Rotation into robot frame
    float dx_r =  cos(theta) * dx + sin(theta) * dy;
    float dy_r = -sin(theta) * dx + cos(theta) * dy;

    // Orientation error
    float dtheta = targetPose.theta - currentPose.theta;
    dtheta = atan2(sin(dtheta), cos(dtheta));

    WayPoint errorCoords = {dx_r, dy_r, dtheta};

    return errorCoords;
}

PalfaBeta getPAlfaBeta(WayPoint errorCoords){
  float distance = sqrt(errorCoords.x*errorCoords.x + errorCoords.y*errorCoords.y);

  float alfa = atan2(errorCoords.y, errorCoords.x);
  alfa = atan2(sin(alfa), cos(alfa)); // Normalize to [-pi, pi]
  float beta = errorCoords.theta - alfa;
  beta = atan2(sin(beta), cos(beta)); // Normalize to [-pi, pi]

  PalfaBeta pAlfaBeta = {distance, alfa, beta};
  return pAlfaBeta;
}




float getVelocity(PalfaBeta pAlfaBeta){
    return kp * pAlfaBeta.distance;
}

float getAngularVelocity(PalfaBeta pAlfaBeta){
    return kAlfa * pAlfaBeta.alfa + kBeta * pAlfaBeta.beta;
}

void MoveToPointUpdate(WayPoint targetPoint){

  WayPoint currentPos = {mainDrive.globalX, mainDrive.globalY, mainDrive.globalTheta};

  WayPoint errorCoords = getError(currentPos, targetPoint);

  PalfaBeta pAlfaBeta = getPAlfaBeta(errorCoords);

  //print error with 2 decimal places
  // Serial.println(f"Error Coords: deltaX: {errorCoords[0]:.2f}, deltaY: {errorCoords[1]:.2f}, deltaTheta: {np.rad2deg(errorCoords[2]):.2f}deg", end=' | ')
  // // print pAlfaBeta with 2 decimal places
  // Serial.println(f"distance: {pAlfaBeta[0]:.2f}, alfa: {np.rad2deg(pAlfaBeta[1]):.2f}deg, beta: {np.rad2deg(pAlfaBeta[2]):.2f}deg" )



  if(pAlfaBeta.distance < 1.0 && abs(errorCoords.theta) < deg2rad(5)){
    Serial.println("Reached waypoint, stopping");
    // mainDrive.StopFollowing();
    isTrackingPoint = false;
    return;
  }

  //print float with 2 decimal places
  //print(f"deltaX: {errorCoords[0]:.2f}, deltaY: {errorCoords[1]:.2f}, deltaTheta: {np.rad2deg(errorCoords[2]):.2f} deg", f"distance: {pAlfaBeta[0]:.2f}, alfa: {np.rad2deg(pAlfaBeta[1]):.2f} deg, beta: {np.rad2deg(pAlfaBeta[2]):.2f} deg" )


  float vel = getVelocity(pAlfaBeta);
  float omega = getAngularVelocity(pAlfaBeta);


  vel = constrain(vel, -vMax, vMax) * max(0, cos(pAlfaBeta.alfa));  // Reduce velocity when not facing the target
  omega = constrain(omega, -omegaMax, omegaMax);


}
