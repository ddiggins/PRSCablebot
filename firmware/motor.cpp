// Generic sensor template
// Can be adapted to support sensors, motors, etc...

// Includes
#include <ArduinoJson.h>
#include "object.h"
#include "motor.h"


int Motor::update(JsonDocument* params){ // Same as doc

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


int Motor::run(){

    if (enabled.value.toInt()){
        Serial.print("{\"id\" : \"");
        Serial.print(id_name());
        Serial.print("\", \"enabled\" : ");
        Serial.print(enabled.value);
        Serial.print(", \"value\" : ");
        Serial.print(4); // Arbitrary value replace with real output
        Serial.println("}");
    }
    return 0;
}


Motor::Motor(String name){
    id.value = name;
    attributes.attrs[0] = &id; // id must always come first
    attributes.attrs[1] = &enabled;
}

String Motor::id_name(){
    return attributes.attrs[0]->value;
}
