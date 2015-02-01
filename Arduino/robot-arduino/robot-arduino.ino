#include <SoftwareSerial.h>
#include <SerialCommand.h>
#include "SDPArduino.h"
#include <Wire.h>

#define boardLED 13 // This is the LED on the Arduino board itself
#define radioPin 8 // This is the pin used to control the radio

// Define motor connectors
#define leftMotor 0
#define rightMotor 1
#define kicker 2

SerialCommand scomm;

int blink = 1;

void setup() { 
  SDPsetup();
  
  // Set input and output pins
  pinMode(boardLED, OUTPUT);
  
  // Set up the serial port
  pinMode(radioPin, OUTPUT); // Initialise the radio
  digitalWrite(radioPin, HIGH);
  Serial.begin(115200); // Run at 115200 baud
  
  Serial.println("radio_initialised");
  
  // Add callbacks for all commands
  scomm.addCommand("forward", command_forward);
  scomm.addCommand("reverse", command_reverse);
  scomm.addCommand("stop", command_stop);
  scomm.addCommand("turn_right", command_turn_right);
  scomm.addCommand("turn_left", command_turn_left);
  scomm.addCommand("kicker_catch", command_kicker_catch);
  scomm.addCommand("kicker_kick", command_kicker_kick);
  scomm.addCommand("kicker_stop", command_kicker_stop);
  scomm.addCommand("led_on", command_led_on); // args: []
  scomm.addCommand("led_off", command_led_off); // args: []
  scomm.addCommand("blink_n_times", command_blink_n_times); // args: [n]
  scomm.addCommand("blink", command_start_blinking); // args: [blinkDelay]
  scomm.addCommand("stop_blinking", command_stop_blinking); // args: []
  scomm.addDefaultHandler(command_unknown);
  
  Serial.println("ready"); 
}

void loop() {
  scomm.readSerial();
}

// Command callback functions
void command_forward() {
  char *arg = scomm.next();
  int motorSpeed = atoi(arg);
  
  motorForward(leftMotor, motorSpeed);
  motorForward(rightMotor, motorSpeed); 
}

void command_reverse() {
  char *arg = scomm.next();
  int motorSpeed = atoi(arg);
  
  motorBackward(leftMotor, motorSpeed);
  motorBackward(rightMotor, motorSpeed);
}

void command_stop() {
  motorStop(leftMotor);
  motorStop(rightMotor); 
}

void command_turn_right() {
  char *arg = scomm.next();
  int motorSpeed = atoi(arg);
  
  motorForward(leftMotor, motorSpeed);
  motorBackward(rightMotor, motorSpeed);
}

void command_turn_left() {
  char *arg = scomm.next();
  int motorSpeed = atoi(arg);
  
  motorForward(rightMotor, motorSpeed);
  motorBackward(leftMotor, motorSpeed);
}

void command_kicker_kick() {
  char *arg = scomm.next();
  int motorSpeed = atoi(arg);
  
  motorForward(kicker, motorSpeed); 
}

void command_kicker_catch() {
  char *arg = scomm.next();
  int motorSpeed = atoi(arg);
  
  motorBackward(kicker, motorSpeed); 
}

void command_kicker_stop() {
  motorStop(kicker); 
}

void command_led_on() {
  Serial.println("LED on");
  digitalWrite(13, HIGH);
}

void command_led_off() {
  Serial.println("LED off");
  digitalWrite(13, LOW); 
}

void command_blink_n_times() {
  char *arg = scomm.next();
  
  int n = atoi(arg);
  
  for (int i = 0; i < n; i++) {
    digitalWrite(boardLED, HIGH);
    delay(500);
    digitalWrite(boardLED, LOW);
    delay(500);
  }
}

void command_start_blinking() {
  char *arg = scomm.next();
  int blinkDelay = atoi(arg);
  
  blink = 1;
  
  while (blink) {
    // scomm.readSerial(); // Because this is infinite, we need to keep checking the serial to see if we need to stop
    if (Serial.available() > 0) {
      return;
    }
    
    digitalWrite(boardLED, HIGH);
    delay(blinkDelay);
    digitalWrite(boardLED, LOW);
    delay(blinkDelay);
  } 
}

void command_stop_blinking() {
  blink = 0;
}

void command_unknown() {
 Serial.println("unknown_command");
}
