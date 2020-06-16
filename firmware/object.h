// A generic object to use when linking different object classes

#ifndef GENERICOBJECT
#define GENERICOBJECT

#include <ArduinoJson.h>
#include <StreamUtils.h>
#include <SoftwareSerial.h>
#include <string.h>


// A generic object that is inherited by specific object types to allow polymorphic
// indexing of connected objects.
// Functions in Generic Object are not defined so the object must be inherited before use
class GenericObject{

    protected:

    // Structure that defines the key:value behavior which is compatible with JSON
    typedef struct Attribute {
        String name;
        String value;

    }Attribute;

    // A container for multiple attributes that can be iterated through
    typedef struct Attributes {
        // Gives each object attributes (change size to fit the maximum needed objects)
        const static int number = 10;
        Attribute* attrs[number];
    } Attributes;

    public:

    // Defines the function of the object while in operation
    // Actions in run will be run each time the run section of main executes
    virtual int run() = 0;

    // Defines how parameters should be updated based on an
    // incoming JsonDocument that matches the object's id
    virtual int update(JsonDocument* params) = 0;

    // Returns the unique id of the object
    virtual String id_name();

};

#endif