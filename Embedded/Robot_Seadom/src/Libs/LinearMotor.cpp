#include "LinearMotor.h"


LinearMotor* LinearMotor::singletonInstance = nullptr;

LinearMotor::LinearMotor(uint8_t port)
    : encoderMotor(port){
}

void LinearMotor::SetupLinearMotor() {

    singletonInstance = this;

    attachInterrupt(encoderMotor.getIntNum(), PulseCheckEncoder, RISING);  // Count pulses on rising edges
    encoderMotor.setPulse(8);
    encoderMotor.setRatio(46.67);
    encoderMotor.setPosPid(1.8,0,1.2);
    encoderMotor.setSpeedPid(0.18,0,0);

    
}



void LinearMotor::MoveHome() {
    
    encoderMotor.moveTo(0);

    // CONFIGURE IF WE NEED AWAIT
    // while (!Encoder_1.isTarPosReached())
    // {
    //     _delay(1);
    // }
    // _delay(1);
}

void LinearMotor::MoveDown() {
    
    encoderMotor.moveTo(2000);

    // CONFIGURE IF WE NEED AWAIT
    // while (!Encoder_1.isTarPosReached())
    // {
    //     _delay(1);
    // }
    // _delay(1);
}


// Special movment commands

void LinearMotor::Update() {
    encoderMotor.loop();
}




void LinearMotor::PulseCheckEncoder() {
    singletonInstance->handleEncoder();
}

void LinearMotor::handleEncoder(void)
{
    // Interrupt handler for left encoder pulse counting.
    if (digitalRead(encoderMotor.getPortB()) == 0)
    {
        encoderMotor.pulsePosMinus(); 
    }
    else
    {
        encoderMotor.pulsePosPlus();  
    }
}
