// Program to control a robot on a cable

// Includes here
#include <ArduinoJson.h>
#include <StreamUtils.h>
#include "interpreter.h"
#include "json.h"
#include "sensor.h"
#include <SoftwareSerial.h>
#include "object.h"


// Test JSON: {"id" : "Sensor1", "enabled" : "1"}


SoftwareSerial client(2, 3); // RX, TX

void setup(){
    // Initialize serial at baud 115200
    Serial.begin(115200);
}

void loop(){

    // Initialize classes and define parameters
    Interpreter interpreter;
    const int capacity = 1000; // Bytes of longest string needed
    DynamicJsonDocument doc(capacity);

    // Create list of sensors and structure to hold them

    typedef struct Sensors{
        const static int number = 1;
        Sensor* items[number]; // Number of sensors
    } Sensors;


    Sensor sensor("Sensor1");

    Sensors sensors;
    sensors.items[0] = &sensor;

    int last_time = 0;


    while(1){

        // Run interpreter

        interpreter.read(&doc);
        const char* id = doc["id"]; // Extract id from json


        for(int i=0; i<sensors.number; i++){
            if (sensors.items[i]->id_name().equals(String(id))){
                sensors.items[i]->update(&doc); // If the id matches then update
            }
        }

        if (millis()-last_time > 1000){ // Read once per second

            for(int i=0; i<sensors.number; i++){
                sensors.items[i]->run();
            }
            last_time = millis();
        }
    }
}
