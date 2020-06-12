// Generic sensor template
// Can be adapted to support sensors, motors, etc...

#ifndef SENSOR
#define SENSOR

// Includes

#include "object.h"
#include <ArduinoJson.h>
#include <string.h>
#include "interpreter.h"
#include "json.h"


class Sensor: public GenericObject{

    protected:

    typedef struct Attribute {
        String name;
        String value;

    }Attribute;


    typedef struct Attributes {
        // Gives each object attributes (change size as needed)
        //TODO: Figure out why number does not work in attrs
        const static int number = 2;
        Attribute* attrs[number];
    } Attributes;

    Attribute enabled = {"enabled", "0"};

    public:


    // Attributes of sensor
    Attribute id = {"id", "Generic Sensor"};

    // Define all attributes of class
    Attributes attributes;


    int run();
    int update(JsonDocument* params);
    Sensor(String name);

};

#endif
