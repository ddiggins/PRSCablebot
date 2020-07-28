// Motor Control Class
// Runs a motor controller that outputs a pwm signal

// Includes
#include <ArduinoJson.h>
#include <Servo.h>
// #include <Encoder.h>
#include <PID_v1.h>
#include "object.h"
#include "motor.h"


int Motor::update(JsonDocument* params) {  // Same as doc

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


int Motor::run() {


    if ((millis()-update_time) > 1000/update_rate.value.toInt()) {
        update_time = millis();
        // // Emergency stop
        // if (!digitalRead(stop_pin)) {
        //     stopped = 1;
        // }

        if (enabled.value.toInt() && !stopped) {

            if (mode.value.toDouble()){
                // Encoder control

                if (!motor.attached()) {
                    motor.attach(motorPWM);
                }

                Input = target.value.toDouble() - encoder->encoder->read(); // Calculate error
                pid->Compute();
                pwm = Output + 1500;
                motor.writeMicroseconds(pwm);
                Serial.print(Output);
                Serial.print(", ");
                Serial.println(Input);

            }

            else{

                // Update Motor speed
                int timeOn = int(speed.value.toDouble()*500.0+1500.0);
                if (!motor.attached()) {
                    motor.attach(motorPWM);
                }
                motor.writeMicroseconds(timeOn);

            }


        } else {
            if (motor.attached()) {
                motor.detach();
            }
        }



        // Prints serial output
        Serial.print(F("{\"id\" : \""));
        Serial.print(id_name());
        Serial.print(F("\", \"enabled\" : "));
        Serial.print(enabled.value);
        Serial.print(F(", \"speed\" : "));
        Serial.print(speed.value);
        Serial.println(F("}"));
    }
}


Motor::Motor(String name, MotorEncoder* encoder_in) {
    id.value = name;
    attributes.attrs[0] = &id;  // id must always come first
    attributes.attrs[1] = &enabled;
    attributes.attrs[2] = &update_rate;
    attributes.attrs[3] = &speed;
    attributes.number = 4;
    pinMode(stop_pin, INPUT_PULLUP);
    encoder = encoder_in;

    pid->SetMode(AUTOMATIC);
    pid->SetOutputLimits(-500, 500);

    // Set sample rate of the PID loop to 100 times per second (Default 10)
    pid->SetSampleTime(10);
}


String Motor::id_name() {
    return attributes.attrs[0]->value;
}
