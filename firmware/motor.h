// Motor Control Class
// Runs a motor controller that outputs a pwm signal

#ifndef MOTOR
#define MOTOR

#include <string.h>
#include <ArduinoJson.h>
#include <Servo.h>
#include "object.h"


// A motor control class
// Inherits from GenericObject and redefines methods to update parameters and run
// Each object must have a unique id as its first attribute so it can be addressed
class Motor: public GenericObject{

 protected:
    Attribute enabled = {"enabled", "0"};
    Attribute speed = {"speed", "1"};
    Attribute update_rate = {"updateRate", "1"};
    int last_time = 0;  // Variable for motor update update_rate
    int update_delay = 1000;  // Milliseconds between sensor printouts
    int update_time = 0;  // Variable for printout timing

    // Pin for the motor and stop
    int motorPWM = 9;
    int stop_pin = 7;
    int stopped = 0; // Whether an estop command was issued

    // Create a servo object for the motor
    Servo motor;

 public:
    // Attributes of sensor
    Attribute id = {"id", "Generic Sensor"};

    // Define all attributes of class
    Attributes attributes;
    
    // Initializes and defines unique id
    Motor(String name);

    // Methods inherited from GenericObject and redefined to fit the characteristic of the object
    int run();
    int update(JsonDocument* params);
    String id_name();

};

#endif
