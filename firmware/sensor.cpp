// Generic sensor template
// Can be adapted to support sensors, motors, etc...

// Includes
#include <ArduinoJson.h>
#include "sensor.h"
// #include "genericObject.h"

int Sensor::update(JsonDocument* params){ // Same as doc

    JsonObject obj = (*params).as<JsonObject>();

    for (JsonPair p : obj){
        for (int i=0; i<attributes.number; i++){  // Go from 1 to exclude id (check that this is correct)
            if (attributes.attrs[i]->name.equals(p.key().c_str())){
                // If the string matches the name of an attribute
                attributes.attrs[i]->value = String (p.value().as<char*>());
            }
        }
    }
    return 0;
}


int Sensor::run(){

    // Describes how the sensor actually works based on the class attributes

    if (enabled.value.toInt()){
        Serial.print("{\"id\" : \"");
        // Serial.print(id.value);
        Serial.print(attributes.attrs[0]->value);
        Serial.print("\", \"enabled\" : ");
        Serial.print(enabled.value);
        Serial.print(", \"value\" : ");
        Serial.print(4); // Arbitrary value replace with real output
        Serial.println("}");
    }
    return 0;
}


Sensor::Sensor(String name){
    // Define sensor attributes outside of class definition
    id.value = name;
    attributes.attrs[0] = &id;
    attributes.attrs[1] = &enabled;
}

String Sensor::id_name(){
    return attributes.attrs[0]->value;
}
