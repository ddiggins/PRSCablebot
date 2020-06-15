// Program to control a robot on a cable

#include <ArduinoJson.h>
#include <StreamUtils.h>
#include "interpreter.h"
#include <SoftwareSerial.h>
#include "object.h"
#include "motor.h"
#include "sensor.h"



// Test JSON: {"id" : "Sensor1", "enabled" : "1"}

// Uncomment to use software serial
// SoftwareSerial client(2, 3); // RX, TX

//Set pin for motor motorDrive
int motorDrive = 9;

void setup(){
    // Initialize serial at baud 115200
    Serial.begin(115200);
    // Set Motor speed and direction control pin.
    pinMode(motorDrive, OUTPUT);
}

void loop(){

    // Initialize classes and define parameters
    Interpreter interpreter;
    const int capacity = 1000; // Bytes of longest string needed
    DynamicJsonDocument doc(capacity);

    // Create list of sensors and structure to hold them
    typedef struct Objects{
        const static int number = 1;
        GenericObject* items[number]; // Number of sensors
    } Objects;


    // Define objects
    Sensor sensor("Sensor1");


    // Add objects to structure
    Objects objects;
    objects.items[0] = &sensor;

    while(1){

        // Run interpreter
        interpreter.read(&doc);
        const char* id = doc["id"]; // Extract id from json

        for(int i=0; i<objects.number; i++){
            if (objects.items[i]->id_name().equals(String(id))){
                objects.items[i]->update(&doc); // If the id matches then update
            }
        }


        for(int i=0; i<objects.number; i++){
            objects.items[i]->run(); // Update each object
        }

    }
}
