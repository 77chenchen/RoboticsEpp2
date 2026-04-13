#include <Servo.h>

Servo myservo;

void setup() {
  myservo.attach(36);   
  myservo.write(90);   
}

void loop() {
}