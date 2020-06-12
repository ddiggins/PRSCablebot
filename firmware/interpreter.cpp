// Interpreter for serial commands
#include <ArduinoJson.h>
#include <StreamUtils.h>
#include <SoftwareSerial.h>
#include <string.h>
#include "interpreter.h"
#include "json.h"
#include "sensor.h"


// TODO: Download libraries
// TODO: Write a function that clears doc

int Interpreter::read(DynamicJsonDocument* doc, JsonObject* root){
     

    // TODO: Read incoming lines from serial
    // Look for Serial.read() function
    char json[] = "";
    String str;

    if (Serial.available() > 0){
        // read the incoming line:
        str = "0";
        str = Serial.readStringUntil('\n');
        Serial.println(str);

        if (str == "0"){return;}
        // Interprets meaning with json
        DeserializationError error = deserializeJson(*doc, str);
        Serial.println(error.c_str());

        // Handles error
        if (error) {
            Serial.print(F("deserializeJson() failed: "));
            Serial.println(error.c_str());
            return 1;
        }

        // Get the JsonObject in the JsonDocument
        *root = doc->to<JsonObject>();
    }
    return 0;
    
}

int Interpreter::clear() {
    // TODO: Clear DynamicJsonDocument
}
