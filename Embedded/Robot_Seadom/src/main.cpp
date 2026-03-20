#include "Libs/GripperLib.h"
#include <Arduino.h>
#include <Wire.h>
#include <ctype.h>
#include "MeMegaPi.h"
#include "Libs/MainDriveLib.h"


Gripper gripper(PORT4A);
MainDrive lineFollower(6, SLOT1, SLOT2);

int executeCommand(String cmd);
void HandleCommands();
void setUpBluetooth();  

void setup()
{
  Serial.begin(115200);
  
  setUpBluetooth();
  lineFollower.SetupLineFollow();
  lineFollower.StopFollowing();

}

void loop()
{ 
  HandleCommands();
  
  
  lineFollower.UpdateMainDrive();
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
      lineFollower.StopFollowing();
    }
    else if (cmd == "start track"){
      lineFollower.ResumeFollowing();
    } 
    else if (cmd == "flip"){
      lineFollower.Flip();
    } 
    else if (cmd == "celebrate"){
      // TODO: Implement Celebration
    }  
    else if (cmd.startsWith("setspeed")){
      // TODO: Implement Speed
    } else {
      Serial.println("Unknown command: " + cmd);
      Serial3.println("Unknown command: " + cmd);
    }

   return 0; 
}