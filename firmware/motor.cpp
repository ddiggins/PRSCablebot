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

        if ((millis()-update_time) > update_delay){
            // Prints serial output
            Serial.print("{\"id\" : \"");
            Serial.print(id_name());
            Serial.print("\", \"enabled\" : ");
            Serial.print(enabled.value);
            Serial.print(", \"speed\" : ");
            Serial.print(speed.value);
            Serial.println("}");
            update_time = millis();
        }

        if ((millis()-last_time) > 20){
            int timeOn = int(speed.value.toDouble()*500.0+1500.0);
            // Serial.println(timeOn);
            last_time = millis();
            digitalWrite(motorPWM, HIGH);
            //TODO: the delay is not ideal so we should think of a better method later
            delayMicroseconds(timeOn);
            digitalWrite(motorPWM, LOW);
        }
    }   
}


Motor::Motor(String name){
    id.value = name;
    attributes.attrs[0] = &id; // id must always come first
    attributes.attrs[1] = &enabled;
    attributes.attrs[2] = &update_rate;
    attributes.attrs[3] = &speed;
    attributes.number = 4;

    // Set Motor speed and direction control pin.
    pinMode(motorPWM, OUTPUT);
}


String Motor::id_name(){
    return attributes.attrs[0]->value;
}
