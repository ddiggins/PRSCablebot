// Interpreter for incoming commands

#ifndef INTERPRETER
#define INTERPRETER

// Includes
#include <ArduinoJson.h>
#include <StreamUtils.h>
#include <SoftwareSerial.h>
#include "interpreter.h"
#include "json.h"
#include "sensor.h"

class Interpreter{

    protected:

    /* Variables/methods to be used only by the interpreter */
    // Allocate memory for StaticJsonDocument
    // StaticJsonDocument<200> doc;





    public:

    // Variables to be used by other classes
    //TODO: Make return return error code
    JsonObject execute(SoftwareSerial client);
};

#endif