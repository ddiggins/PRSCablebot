/* Experiment to determine optimal motor control method for dc motor with encoder */

#include <Servo.h>
#include <Encoder.h>
#include <PID_v1.h>



Servo motor;
int motorPin = 9;
int pin1 = 2;
int pin2 = 3;

double target = 2;
int error = 0;
int pwm = 0;
String str;
long last_time = 0;
double last_position = 0;
double new_position = 0;
double speed = 0;
long new_time = 0;


//Global variables for PID input/output
double Setpoint, Input, Output = 0.0;


//Global PID tuning parameters
double Kp=100, Ki=50, Kd=0;

// Define pid class with pointers to global variables
PID pid(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);



void setup(){
    // Initialize serial at baud 115200
    Serial.begin(115200);

    pid.SetMode(AUTOMATIC);
    pid.SetOutputLimits(-500, 500);

    // Set sample rate of the PID loop to 100 times per second (Default 10)
    pid.SetSampleTime(10);
    
}


void loop(){

    motor.attach(motorPin);
    Encoder* encoder = new Encoder(pin1, pin2);


    while (1){

        if (Serial.available() > 0) {
            // read the incoming byte:
            target = Serial.readStringUntil('\n').toDouble();
        }

        last_position = encoder->read();
        last_time = millis();



        // Input = target - encoder->read(); // Calculate error
        Input = target - speed; // Calculate error
        pid.Compute();

        pwm = Output + 1500;

        // if (1505<pwm && pwm<1526){
        //     pwm = 1526;
        // }

        // if (1495<pwm && pwm<1497){
        //     pwm = 1495;
        // }

        motor.writeMicroseconds(pwm);

        Serial.print("Encoder: ");
        Serial.print(encoder->read());
        Serial.print("   Input: ");
        Serial.print(Input);
        Serial.print("    Output: ");
        Serial.print(Output);
        Serial.print("    Speed: ");
        Serial.println(speed);


        new_position = encoder->read();
        new_time = millis();

        speed = (new_position - last_position) / ((double) new_time - (double) last_time);

    }


}