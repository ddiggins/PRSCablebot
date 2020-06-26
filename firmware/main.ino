// Program to control a robot on a cable

#include <ArduinoJson.h>
#include <StreamUtils.h>
#include "interpreter.h"
#include <SoftwareSerial.h>
#include "object.h"
#include "motor.h"
#include "sensor.h"
#include "tempSensor.h"
#include "leakSensor.h"



// Test JSON: {"id" : "Sensor1", "enabled" : "1"}
// Test for motor: {"id":"Motor1","speed":".5"}

// Uncomment to use software serial
// SoftwareSerial client(2, 3); // RX, TX



void setup(){
    // Initialize serial at baud 115200
    Serial.begin(115200);
    
}

void loop(){

    // Initialize classes and define parameters
    Interpreter interpreter;
    const int capacity = 100; // Bytes of longest string needed
    DynamicJsonDocument doc(capacity);

    // Create list of sensors and structure to hold them
    typedef struct Objects{
        const static int number = 5; // Number of sensors
        GenericObject* items[number];
    } Objects;


    // Define objects
    Sensor sensor("Sensor1");
    Motor motor("Motor1");
    TempSensor tempsensor("tempsensor");
    LeakSensor foreleak("foreleak", 13);
    LeakSensor aftleak("aftleak", 12);

    // Add objects to structure
    Objects objects;
    objects.items[0] = &sensor;
    objects.items[1] = &motor;
    objects.items[2] = &tempsensor;
    objects.items[3] = &foreleak;
    objects.items[4] = &aftleak;

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
