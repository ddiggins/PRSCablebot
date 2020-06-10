// Interpreter for incoming commands

#ifndef INTERPRETER
#define INTERPRETER

// Includes

#include "interpreter.h"
#include "json.h"
#include "sensor.h"

class Interpreter{

    protected:

    // Variables/methods to be used only by the interpreter

    public:

    // Variables to be used by other classes
    int execute();
};

#endif