// Program to control a robot on a cable

// Includes here
#include <ArduinoJson.h>
#include <StreamUtils.h>
#include "interpreter.h"
#include "json.h"
#include "sensor.h"
#include <SoftwareSerial.h>


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
    JsonObject root;

    // Create list of sensors and structure to hold them

    typedef struct Sensors{
        int number = 1;
        Sensor* items[1]; // Number of sensors
    } Sensors;

    Sensor sensor("Sensor1");

    Sensors sensors;
    sensors.items[0] = &sensor;

    int last_time = 0;



    

    while(1){




        // Run interpreter

        interpreter.read(&doc, &root);
        const char* id = doc["id"];
        // if (String(id) != ""){
        // Serial.print("id is:");
        // Serial.println(String(id));
        // }


        // for (JsonObject::iterator it=root.begin(); it!=root.end(); ++it) {
        //     Serial.println(it->key().c_str()); // is a JsonString
        //     // Serial.println(it->value().as<char*>()); // is a JsonVariant
        // }


        for(int i=0; i<sensors.number; i++){
            // Serial.println(sensors.items[i]->attributes.attrs[0]->name);
            if (sensors.items[i]->attributes.attrs[0]->value.equals(String(id))){
                // Serial.println("Matched");
                sensors.items[i]->update(&doc);
            }
        }

        // if (millis()-last_time > 1000){

            for(int i=0; i<sensors.number; i++){
                sensors.items[i]->run();
            }
        //     last_time = millis();
        // }

    }

    // // Sensor sensor;

    // while (1){
    //     sensor.run();
    // }



}