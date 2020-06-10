// Program to control a robot on a cable

// Includes here
#include "interpreter.h"
#include "json.h"
#include "sensor.h"

void setup(){
    // Initialize serial at baud 115200
    Serial.begin(115200);
}

void loop(){

    // Initialize classes and define parameters
    Interpreter interpreter();

    

    while(1){

        // Run interpreter
        interpreter.execute();
    }


}