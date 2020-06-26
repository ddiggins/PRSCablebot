// Leak sensor that checks conductivity to determine if there is a leak

#ifndef LEAKSENSOR
#define LEAKSENSOR


#include <ArduinoJson.h>
#include <string.h>
#include "object.h"


// An example of a generic sensor type.
// Inherits from GenericObject and redefines methods to update parameters and run
// Each object must have a unique id as its first attribute so it can be addressed
class LeakSensor: public GenericObject{

 protected:
    Attribute enabled = {"enabled", "0"};
    Attribute update_rate = {"updateRate", "1"};
    unsigned long last_time = 0; // Variable for timing
    int pin;

 public:

    // Attributes of sensor
    Attribute id = {"id", "Generic Sensor"};

    // Define all attributes of class
    Attributes attributes;
    
    // Creates a Sensor object and assigns a unique id to the object
    // pin is the pin number the sensor is plugged into
    LeakSensor(String name, int pin);

    // Methods inherited from GenericObject and redefined to fit the characteristic of the object
    int run();
    int update(JsonDocument* params);
    String id_name();

};

#endif
