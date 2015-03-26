#include <SoftwareSerial.h>
#include <SerialCommand.h>
#include "SDPArduino.h"
#include <Wire.h>
#include <stdlib.h>

#define boardLED 13 // This is the LED on the Arduino board itself
#define radioPin 8 // This is the pin used to control the radio

// Define motor connectors
#define leftMotor 0
#define rightMotor 1
#define kicker 2

// Define event buffer paramters
#define EVENT_BUFFER_SIZE 50

SerialCommand scomm;

int blink = 1;
String kicker_position = "open";

namespace event_loop {
  struct command_entry {
    int motor;
    int speed;
    unsigned long start_time;
    bool todo;
  };
  
  struct command_entry event_buffer[EVENT_BUFFER_SIZE];
  
  void add_command_head(int motor, int speed, unsigned long start_time) {
   // Loop through the array and put this command in the first non-todo
   int i;
   int empty_slot = -1;
   for (i = 0; i < EVENT_BUFFER_SIZE; i++) {
     if (event_buffer[i].todo == false) {
       empty_slot = i;
       break;
     }
   }
   
   // If there is no empty slot, drop the command and print error to serial
   if (empty_slot == -1) {
     Serial.println("error: command buffer full, command dropped");
     onerror();
     return;
   }
      
   event_buffer[empty_slot].motor = motor;
   event_buffer[empty_slot].speed = speed;
   event_buffer[empty_slot].start_time = start_time;
   event_buffer[empty_slot].todo = true;
  }
  
  // Sets the value of "todo" to false in each buffer entry
  void initialise_buffer() {
    int i;
    for (i = 0; i < EVENT_BUFFER_SIZE; i++)
    {
      event_buffer[i].todo = false;
    }
  }
  
  void process_list() {
    int i;
    for (i = 0; i < EVENT_BUFFER_SIZE; i++) {
      if (event_buffer[i].todo && event_buffer[i].start_time <= millis()) {
        set_motor_speed(event_buffer[i].motor, event_buffer[i].speed);
  
        // Set todo to false so this buffer slot can be reused
        event_buffer[i].todo = false;
      }
    }
  }
}

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
  scomm.addCommand("s", store_motor_action); // args: [motor, speed, delay]
  scomm.addCommand("p", prepare_catch); // args: []
  scomm.addCommand("k", kick); // args: [speed]
  scomm.addCommand("c", catch_ball); // args: [speed]
  scomm.addCommand("ping6", ping);
  scomm.addCommand("led_on", command_led_on); // args: []
  scomm.addCommand("led_off", command_led_off); // args: []
  scomm.addCommand("blink_n_times", command_blink_n_times); // args: [n]
  scomm.addCommand("blink", command_start_blinking); // args: [blinkDelay]
  scomm.addCommand("stop_blinking", command_stop_blinking); // args: []
  scomm.addDefaultHandler(command_unknown);

  open_kicker();
        
  Serial.println("ready"); 
}

int blink_count = 0;
boolean led_on = false;
int blink_interval = 20000;
void loop() {
  if (blink_count == blink_interval) {
    if (led_on) {
      digitalWrite(boardLED, LOW);
      led_on = false;
    } else {
      digitalWrite(boardLED, HIGH);
      led_on = true;
    }
    blink_count = 0;
  }
  blink_count++;
  
  scomm.readSerial();
    
  event_loop::process_list();
}

// Command callback functions
void store_motor_action() {
//    Serial.println("ack6");
    char *motorarg = scomm.next();
    char *speedarg = scomm.next();
    char *delayarg = scomm.next();

    int motor = atoi(motorarg);
    int speed = atoi(speedarg);
    int delay = atoi(delayarg);
    
    // Only use the event loop if there is a delay involved
    if (delay == 0) {
      set_motor_speed(motor, speed);
    } else {
      event_loop::add_command_head(motor, speed, millis()+delay);
    }
}

void onerror() {
  blink_interval = 2000;
}

void prepare_catch() {
//  Serial.println("ack6");
  
  if (kicker_position == "prepared") {
    return;
  }
  
  // Start the kicker immediately, after 1 second stop it and then reverse it at a reduced speed then stop it 200ms after that
  event_loop::add_command_head(kicker, 100, millis());
  event_loop::add_command_head(kicker, 0, millis()+1000);
  event_loop::add_command_head(kicker, -40, millis()+1500);
  event_loop::add_command_head(kicker, 0, millis()+1700);
  
  kicker_position = "prepared";
}

void kick() {
//  Serial.println("ack6");
  char *speedarg = scomm.next();
  
  if (kicker_position == "open") {
    return;
  }
  
  int speed = atoi(speedarg);
  event_loop::add_command_head(kicker, speed, millis());
  event_loop::add_command_head(kicker, 0, millis()+1000);
  
  kicker_position = "open";
}

void open_kicker() {
  motorForward(kicker, 100);
  delay(1000);
  motorStop(kicker);
  
  kicker_position = "open";
}


void ping(){
  Serial.println("ack6");
}

void catch_ball() {
//  Serial.println("ack6");
  char *speedarg = scomm.next();
  
  if (kicker_position == "closed") {
    return;
  }
  
  int speed = atoi(speedarg);
  
  // Start the catch immediately, after 1 second stop the motor
  event_loop::add_command_head(kicker, -1 * speed, millis());
  event_loop::add_command_head(kicker, 0, millis()+1000);
  
  kicker_position = "closed";
}

void set_motor_speed(int motor, int speed) {
  if (speed > 0) {
      motorForward(motor, speed);
    } else if (speed < 0) {
      motorBackward(motor, abs(speed));
    } else if (speed == 0) {
      motorStop(motor);
    }
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
