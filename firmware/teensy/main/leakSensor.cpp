// Leak sensor that checks conductivity to determine if there is a leak

#include <ArduinoJson.h>
#include "leakSensor.h"

int LeakSensor::update(JsonDocument* params){ // Same as doc

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


int LeakSensor::run(){

    if ((millis()-last_time) > (1000/update_rate.value.toInt())){

        if (enabled.value.toInt()){
            Serial.print(F("{\"id\" : \""));
            Serial.print(id_name());
            Serial.print(F("\", \"enabled\" : "));
            Serial.print(enabled.value);
            Serial.print(F("\", \"leak\" : "));
            Serial.print(!digitalRead(pin));
            Serial.println(F("}"));
        }
        last_time = millis();
    }
    return 0;
}


LeakSensor::LeakSensor(String name, int input_pin){
    id.value = name;
    attributes.attrs[0] = &id; // id must always come first
    attributes.attrs[1] = &enabled;
    attributes.attrs[2] = &update_rate;
    attributes.number = 3;

    // Set pin
    pin = input_pin;
    pinMode(pin, INPUT_PULLUP);
}

String LeakSensor::id_name(){
    return attributes.attrs[0]->value;
}
