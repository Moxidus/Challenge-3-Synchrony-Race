#ifndef LINEAR_MOTOR_H
#define LINEAR_MOTOR_H

#include "MeMegaPi.h"
#include <Arduino.h>

class LinearMotor {
public:
    static LinearMotor* singletonInstance;

    LinearMotor(uint8_t slot);

    static void PulseCheckEncoder();
    void handleEncoder();

    void Update();
    void SetupLinearMotor();
    void MoveDown();
    void MoveHome();
    void SetHome();

private:
    MeEncoderOnBoard encoderMotor;
};

#endif