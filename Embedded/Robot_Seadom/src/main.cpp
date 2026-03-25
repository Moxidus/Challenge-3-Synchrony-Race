#include "Libs/GripperLib.h"
#include <Arduino.h>
#include <Wire.h>
#include <ctype.h>
#include "MeMegaPi.h"
#include "Libs/MainDriveLib.h"



// SELECT ROBOT YOU ARE PROGRAMMING!!!
#define MOTHER_ROBOT
// #define DAUGHTER_ROBOT

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
float KP = 0.3;
float KI = 0.000;
float KD = 0.2;
bool invertForward = true;
#endif

int executeCommand(String cmd);
void HandleCommands();
void setUpBluetooth();  

void setup()
{
  Serial.begin(115200);
  
  setUpBluetooth();
  mainDrive.SetupLineFollow(KP, KI, KD, invertForward);
  mainDrive.StopFollowing();

}

void loop()
{ 
  HandleCommands();
  
  
  mainDrive.UpdateMainDrive();
  gripper.update();

  delay(1);
}

void setUpBluetooth(){
  Serial3.begin(115200); 
  Serial.println("Bluetooth Start!");
}

void HandleCommands(){
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

int executeCommand(String cmd){
    if (cmd == "close grip"){
      gripper.close();
    }
    else if (cmd == "open grip"){
      gripper.open();
    }
    else if (cmd == "stop track"){
      mainDrive.StopFollowing();
    }
    else if (cmd == "start track"){
      mainDrive.ResumeFollowing();
    } 
    else if (cmd == "flip"){
      mainDrive.Flip();
    } 
    else if (cmd == "celebrate"){
      // TODO: Implement Celebration
    }  
    else if (cmd.startsWith("setspeed")){
      cmd.replace("setspeed", "");
      int val = cmd.toInt();
      mainDrive.SetDefaultSpeed(val);
      
    } else {
      Serial.println("Unknown command: " + cmd);
      Serial3.println("Unknown command: " + cmd);
    }

   return 0; 
}