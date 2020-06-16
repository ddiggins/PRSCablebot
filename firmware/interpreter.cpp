// Interpreter for serial commands

#include <ArduinoJson.h>
#include <StreamUtils.h>
#include <SoftwareSerial.h>
#include <string.h>
#include "interpreter.h"


int Interpreter::read(DynamicJsonDocument* doc){

    if (Serial.available() > 0){
        
        // read the incoming line:
        str = Serial.readStringUntil('\n');

        if (str == "0"){return;} // Catches blank lines

        // Interprets meaning with json
        DeserializationError error = deserializeJson(*doc, str);

        // Handles json reading errors
        if (error) {
            Serial.print(F("deserializeJson() failed: "));
            Serial.println(error.c_str());
            return 1;
        }
    }
    return 0;
    
}

int Interpreter::clear(DynamicJsonDocument* doc) {
    doc->clear();
}
