// Interpreter for incoming commands

#ifndef INTERPRETER
#define INTERPRETER

#include <ArduinoJson.h>
#include <StreamUtils.h>
#include <SoftwareSerial.h>
#include <string.h>
#include "interpreter.h"
#include "sensor.h"

// Handles reading commands from serial and managing the interpretation of JSON into usable types
// Use the clear() method to free memory used by ArduinoJSON
class Interpreter{

    protected:

    char json[] = "";
    String str;

    public:

    // Reads one line from serial and adds its contents to a DynamicJsonDocument if possible
    // If reading fails prints the appropriate error code to serial and exits without updating the document
    int read(DynamicJsonDocument* doc);

    // Deallocates a DynamicJsonDocument 
    int clear(DynamicJsonDocument* doc);
};

#endif