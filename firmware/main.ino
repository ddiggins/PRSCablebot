// Program to control a robot on a cable

// Includes here
#include "interpreter.h"
#include "json.h"
#include "sensor.h"
#include <SoftwareSerial.h>

SoftwareSerial client(2, 3); // RX, TX

void setup(){
    // Initialize serial at baud 115200
    Serial.begin(115200);

    // Initialize software serial at baud 4800
    client.begin(4800);

}

void loop(){

    // Initialize classes and define parameters
    Interpreter interpreter;

    

    while(1){

        // Run interpreter
        interpreter.execute(client);
    }

    // Sensor sensor;

    // while (1){
    //     sensor.run();
    // }



}