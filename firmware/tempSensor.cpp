// Firmware for the Si7201 temp/humidity sensor

#include <ArduinoJson.h>
#include <Adafruit_Si7021.h>
#include "tempSensor.h"

int TempSensor::update(JsonDocument* params){ // Same as doc

    // Interpret the document to an indexable object (JsonObject is a reference to the document not a copy)
    JsonObject obj = (*params).as<JsonObject>();

    for (JsonPair p : obj){  // Iterate through all json pairs
        for (int i=0; i<attributes.number; i++){  // Go from 1 to exclude id
            if (attributes.attrs[i]->name.equals(p.key().c_str())){
                // If the string matches the name of an attribute
                attributes.attrs[i]->value = String (p.value().as<char*>());
            }
        }
    }
    return 0;
}


int TempSensor::run(){

    if ((millis()-last_time) > (1000/update_rate.value.toInt())){

        if (enabled.value.toInt()){
            Serial.print(F("{\"id\" : \""));
            Serial.print(id_name());
            Serial.print(F("Temp"));
            Serial.print(F("\", \"enabled\" : "));
            Serial.print(enabled.value);
            Serial.print(F(", \"temperature\" : "));
            Serial.print(sensor.readTemperature()); 
            Serial.print(F("{\"id\" : \""));
            Serial.print(id_name());
            Serial.print(F("Humidity"));
            Serial.print(F("\", \"enabled\" : "));
            Serial.print(enabled.value);
            Serial.print(F(", \"humidity\" : "));
            Serial.print(sensor.readHumidity()); 
            Serial.println(F("}"));
        }
        last_time = millis();
    }
    return 0;
}


TempSensor::TempSensor(String name){
    id.value = name;
    attributes.attrs[0] = &id; // id must always come first
    attributes.attrs[1] = &enabled;
    attributes.attrs[2] = &update_rate;
    attributes.number = 3;

    // Initialize sensor
    if (!sensor.begin()){
        Serial.println(F("Error: Unable to find temp/humidity sensor"));
    }
}

String TempSensor::id_name(){
    return attributes.attrs[0]->value;
}
