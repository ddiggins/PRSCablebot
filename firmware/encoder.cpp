// Motor Control Class
// Runs a motor controller that outputs a pwm signal

// Includes
#include <ArduinoJson.h>
#include <Encoder.h>
#include "object.h"
#include "encoder.h"


int MotorEncoder::update(JsonDocument* params) {  // Same as doc

    // Interpret the document to an indexable object (JsonObject is a reference to the document not a copy)
    JsonObject obj = params->as<JsonObject>();

    for (JsonPair p : obj) {  // Iterate through all json pairs
        for (int i = 0; i < attributes.number; i++) {
            if (attributes.attrs[i]->name.equals(p.key().c_str())) {
                // If the string matches the name of an attribute
                attributes.attrs[i]->value = String(p.value().as<char*>());
            }
        }
    }
    return 0;
}


int MotorEncoder::run() {

    if ((millis()-update_time) > 1000/update_rate.value.toInt()) {

        if (enabled.value.toInt()) {

            // Prints serial output
            Serial.print("{\"id\" : \"");
            Serial.print(id_name());
            Serial.print("\", \"enabled\" : ");
            Serial.print(enabled.value);
            Serial.print(", \"position\" : ");
            Serial.print(encoder->read());
            Serial.println("}");
        }
    update_time = millis();
    }
}


MotorEncoder::MotorEncoder(String name) {
    id.value = name;
    attributes.attrs[0] = &id;  // id must always come first
    attributes.attrs[1] = &enabled;
    attributes.attrs[2] = &update_rate;
    attributes.number = 3;
}


String MotorEncoder::id_name() {
    return attributes.attrs[0]->value;
}
