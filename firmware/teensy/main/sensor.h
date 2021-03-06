// Generic sensor template
// Can be adapted to support sensors, motors, etc...

#ifndef SENSOR
#define SENSOR


#include <ArduinoJson.h>
#include <string.h>
#include "object.h"


// An example of a generic sensor type.
// Inherits from GenericObject and redefines methods to update parameters and run
// Each object must have a unique id as its first attribute so it can be addressed
class Sensor: public GenericObject{

 protected:
    Attribute enabled = {"enabled", "0"};
    Attribute update_rate = {"updateRate", "1"};
    unsigned long last_time = 0; // Variable for timing


 public:

    // Attributes of sensor
    Attribute id = {"id", "Generic Sensor"};

    // Define all attributes of class
    Attributes attributes;
    
    // Creates a Sensor object and assigns a unique id to the object
    Sensor(String name);

    // Methods inherited from GenericObject and redefined to fit the characteristic of the object
    int run();
    int update(JsonDocument* params);
    String id_name();

};

#endif
