// Motor Control Class
// Runs a motor controller that outputs a pwm signal

#ifndef ENCODER
#define ENCODER

#include <string.h>
#include <ArduinoJson.h>
//#include </home/colin/Downloads/arduino-1.8.9/hardware/teensy/avr/libraries/Encoder/Encoder.h>
//#include <Encoder.h>
#include "QuadEncoder.h"
#include "object.h"


// A motor control class
// Inherits from GenericObject and redefines methods to update parameters and run
// Each object must have a unique id as its first attribute so it can be addressed
class MotorEncoder: public GenericObject{

 protected:
    Attribute enabled = {"enabled", "0"};
    Attribute update_rate = {"updateRate", "1"};
    unsigned long last_time = 0;  // Variable for motor update update_rate
    int update_delay = 1000;  // Milliseconds between sensor printouts
    unsigned long update_time = 0;  // Variable for printout timing

    int pin1 = 2;
    int pin2 = 3;


 public:

    // Create a servo object for the motor
    QuadEncoder* encoder= new QuadEncoder(1, 0, 1, 0, 4);
    // Attributes of sensor
    Attribute id = {"id", "Generic Sensor"};

    // Define all attributes of class
    Attributes attributes;
    
    // Initializes and defines unique id
    MotorEncoder(String name);

    // Methods inherited from GenericObject and redefined to fit the characteristic of the object
    int run();
    int update(JsonDocument* params);
    String id_name();

};

#endif
