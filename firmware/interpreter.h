// Interpreter for incoming commands

#ifndef INTERPRETER
#define INTERPRETER

// Includes
#include <ArduinoJson.h>
#include <StreamUtils.h>
#include <SoftwareSerial.h>
#include <string.h>
#include "interpreter.h"
#include "json.h"
#include "sensor.h"

class Interpreter{

    protected:

    /* Variables/methods to be used only by the interpreter */
    // Allocate memory for DynamicJsonDocument
    // TODO: Research Memory Alocation





    public:

    // Variables to be used by other classes
    int read(DynamicJsonDocument* doc, JsonObject* root);
    // TODO: Write Clear DynamicJsonDocument Function
    int clear();
};

#endif