// Motor Control Class
// Runs a motor controller that outputs a pwm signal

#ifndef MOTOR
#define MOTOR

#include <string.h>
#include <ArduinoJson.h>
#include <Servo.h>
// #include <Encoder.h>
#include <PID_v1.h>
#include "object.h"
#include "encoder.h"


// A motor control class
// Inherits from GenericObject and redefines methods to update parameters and run
// Each object must have a unique id as its first attribute so it can be addressed
class Motor: public GenericObject{

 protected:
    Attribute enabled = {"enabled", "0"};
    Attribute speed = {"speed", "1"};
    Attribute mode = {"mode", "1"}; // Possible modes are speed (0) and position (1)
    Attribute update_rate = {"updateRate", "1"};
    Attribute target = {"target", "0"}; // Target to run to (steps)
    unsigned long last_time = 0;  // Variable for motor update update_rate
    int update_delay = 1000;  // Milliseconds between sensor printouts
    unsigned long update_time = 0;  // Variable for printout timing
    unsigned long update_time_fast = 0;

    // Pin for the motor
    int motorPWM = 9;
    int stop_pin = 7;
    int stopped = 0;
    int pwm = 0; // pwm frequency

    // Create a servo object for the motor
    Servo motor;

    MotorEncoder* encoder;


    // pwm

    //Global variables for PID input/output
    double Setpoint, Input, Output = 0.0;

    //Global PID tuning parameters
    double Kp=1, Ki=0.05, Kd=0.01;

    // Define pid class with pointers to global variables
    PID* pid = new PID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

 public:
    // Attributes of sensor
    Attribute id = {"id", "Generic Sensor"};

    // Define all attributes of class
    Attributes attributes;
    
    // Initializes and defines unique id
    Motor(String name, MotorEncoder* encoder_in);

    // Methods inherited from GenericObject and redefined to fit the characteristic of the object
    int run();
    int update(JsonDocument* params);
    String id_name();

};

#endif
