// Generic sensor template
// Can be adapted to support sensors, motors, etc...

// Includes

#include <ArduinoJson.h>
#include "sensor.h"

int Sensor::update(JsonObject params){



    for (JsonPair p : params){
        for (int i=0;i<attributes.number;i++){
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

    if (enabled.value){
        Serial.print('{"id" : "');
        Serial.print(id.value);
        Serial.print('", "value" : ');
        Serial.print(enabled.value);
        Serial.println('}');
    }

    return 0;
}

Sensor::Sensor(){
    // typedef struct Book{
    //     int val;
    // }Book:

    // Book book;
    // book.val=2;

    attributes.attrs[0] = &id;
    attributes.attrs[1] = &enabled;

}
