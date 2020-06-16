// Generic sensor template
// Can be adapted to support sensors, motors, etc...

#ifndef MOTOR
#define MOTOR

// Includes

#include "object.h"
#include <ArduinoJson.h>
#include <string.h>


// An example of a generic sensor type.
// Inherits from GenericObject and redefines methods to update parameters and run
// Each object must have a unique id as its first attribute so it can be addressed
class Motor: public GenericObject{

    protected:
    Attribute enabled = {"enabled", "0"};
    Attribute speed = {"speed", "1"};
    Attribute update_rate = {"updateRate", "100"};
    int last_time = 0; // Variable for motor update update_rate
    int update_delay = 1000; // Milliseconds between sensor printouts
    int update_time = 0; // Variable for printout timing

    // Pulse Width Modulation pin for the motor 
    int motorPWM = 9;
    

    public:
    // Attributes of sensor
    Attribute id = {"id", "Generic Sensor"};
    
    // Define all attributes of class
    Attributes attributes;
    
    // Creates a Sensor object and assigns a unique id to the object
    Motor(String name);

    // Methods inherited from GenericObject and redefined to fit the characteristic of the object
    int run();
    int update(JsonDocument* params);
    String id_name();

};

#endif
