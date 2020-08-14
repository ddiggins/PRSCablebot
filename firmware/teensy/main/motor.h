// Motor Control Class
// Runs a motor controller that outputs a pwm signal

#ifndef MOTOR
#define MOTOR

#include <string.h>
#include <ArduinoJson.h>
//#include </home/colin/Downloads/arduino-1.8.9/hardware/teensy/avr/libraries/Servo/Servo.h>
#include<Servo.h>
// #include <Encoder.h>
#include <PID_v1.h>
#include "object.h"
#include "encoder.h"


// A motor control class
// Inherits from GenericObject and redefines methods to update parameters and run
// Each object must have a unique id as its first attribute so it can be addressed
class Motor: public GenericObject{

 protected:
    Attribute enabled = {"enabled", "0"};
    Attribute speed = {"speed", "1"};
    Attribute mode = {"mode", "1"}; // Possible modes are power (0), position (1), and speed (2)
    Attribute update_rate = {"updateRate", "1"};
    Attribute target = {"target", "1000.0"}; // Target to run to (steps)
    unsigned long last_time = 0;  // Variable for motor update update_rate
    int update_delay = 1000;  // Milliseconds between sensor printouts
    unsigned long update_time = 0;  // Variable for printout timing
    unsigned long update_time_fast = 0;

    // Pin for the motor
    int motorPWM = 9;
    int stop_pin = 7;
    int stopped = 0;
    int pwm = 0; // pwm frequency
    float max_accel = 3;
    int last_pwm = 0;


    // Variables for speed pid
    long last_time_s = 1;
    double last_position_s = 0;
    double new_position_s = 0;
    double speed_s = 0;
    long new_time_s = 0;

    // Create a servo object for the motor
    Servo motor;

    MotorEncoder* encoder;

    //Global variables for PID input/output
    double Input_p, Output_p = 0.0;
    double Setpoint_p= 0.0;
    double Input_s, Output_s = 0.0;
    double Setpoint_s= 0.0;
   //  //Global PID tuning parameters
    double Kp_p=1, Ki_p=0.05, Kd_p=0.01;
   // double Kp_p=1, Ki_p=0, Kd_p=0;
    double Kp_s=70, Ki_s=50, Kd_s=0;
    // Define pid class with pointers to global variables
    PID* pid_p = new PID(&Input_p, &Output_p, &Setpoint_p, Kp_p, Ki_p, Kd_p, DIRECT);
   //  PID* pid_p = new PID(&Input_p, &Output_p, &Setpoint_p, Kp_p, Ki_p, Kd_p, DIRECT);
    PID* pid_s = new PID(&Input_s, &Output_s, &Setpoint_s, Kp_s, Ki_s, Kd_s, DIRECT);

 public:
    // Attributes of sensor
    Attribute id = {"id", "Generic Sensor"};

    // Define all attributes of class
    Attributes attributes;
    
    // Initializes and defines unique id
    Motor(String name, MotorEncoder* encoder_in);

    // Methods inherited from GenericObject and redefined to fit the characteristic of the object
    int run();
    int update(JsonDocument* params);
    String id_name();

};

#endif
