// Interpreter for serial commands
#include <ArduinoJson.h>
#include <StreamUtils.h>
#include <SoftwareSerial.h>
#include "interpreter.h"
#include "json.h"
#include "sensor.h"

// TODO: Download libraries
// TODO: Are variables initalized in the right place?
// TODO: Ensure deserializeJson only goes through one json document
// TODO: Do we need to create new documents for every json file

JsonObject Interpreter::execute(SoftwareSerial client){
    // Define JsonDocument
    StaticJsonDocument<200> doc;

    // Read incoming lines from serial
    ReadLoggingStream loggingStream(Serial, Serial);
    
    // Interprets meaning with json
    DeserializationError error = deserializeJson(doc, loggingStream);

    // Handels error
    if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.c_str());
        
        // Flush all bytes in client SoftwareSerial port buffer
        while (client.available() > 0){
            client.read();
        }

        return;
    }

    // Get the JsonObject in the JsonDocument
    JsonObject root = doc.to<JsonObject>();
    return root;
}
