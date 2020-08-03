// Firmware for the Si7201 temp/humidity sensor

#ifndef TEMPSENSOR
#define TEMPSENSOR


#include <ArduinoJson.h>
#include <string.h>
//#include <Adafruit_Si7021.h>
#include <Si7021.h> // Teensy version
#include "object.h"



// An example of a generic sensor type.
// Inherits from GenericObject and redefines methods to update parameters and run
// Each object must have a unique id as its first attribute so it can be addressed
class TempSensor: public GenericObject{

 protected:
    Attribute enabled = {"enabled", "0"};
    Attribute update_rate = {"updateRate", "1"};
    unsigned long last_time = 0; // Variable for timing
    SI7021* sensor = new SI7021();

 public:

    // Attributes of sensor
    Attribute id = {"id", "Generic Sensor"};

    // Define all attributes of class
    Attributes attributes;
    
    // Creates a Sensor object and assigns a unique id to the object
    TempSensor(String name);

    // Methods inherited from GenericObject and redefined to fit the characteristic of the object
    int run();
    int update(JsonDocument* params);
    String id_name();

};

#endif
