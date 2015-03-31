#include <SoftwareSerial.h>
#include <SerialCommand.h>
#include "SDPArduino.h"
#include <Wire.h>
#include <stdlib.h>

#define boardLED 13 // This is the LED on the Arduino board itself
#define radioPin 8 // This is the pin used to control the radio

// Define sensor digital pins
#define reedPin 3
#define prepareReedPin 5

// Define motor connectors
#define leftMotor 0
#define rightMotor 1
#define kicker 2

// Define event buffer paramters
#define EVENT_BUFFER_SIZE 10
#define PREPARE_SPEED -25

SerialCommand scomm;

int blink = 1;
String kicker_position = "open";
boolean kicker_running = false;

namespace event_loop {
  struct command_entry {
    int motor;
    int speed;
    unsigned long start_time;
    int reed_pin;
    int trigger_state;
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
   event_buffer[empty_slot].reed_pin = -1;
   event_buffer[empty_slot].trigger_state = LOW;
  }
  
  void add_command_pin_trigger(int motor, int speed, int reed_pin, int trigger_state, unsigned long do_after) {
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
   event_buffer[empty_slot].start_time = do_after;
   event_buffer[empty_slot].todo = true;
   event_buffer[empty_slot].reed_pin = reed_pin;
   event_buffer[empty_slot].trigger_state = trigger_state;
  }
  
  // Sets the value of "todo" to false in each buffer entry
  void initialise_buffer() {
    int i;
    for (i = 0; i < EVENT_BUFFER_SIZE; i++)
    {
      event_buffer[i].todo = false;
      event_buffer[i].reed_pin = -1;
      event_buffer[i].start_time = -1;
      event_buffer[i].trigger_state = LOW;
    }
  }
  
  void process_list() {
    int i;
    for (i = 0; i < EVENT_BUFFER_SIZE; i++) {       
      if (event_buffer[i].todo && (event_buffer[i].start_time == -1 || event_buffer[i].start_time <= millis())) {
        if (event_buffer[i].reed_pin != -1) {
          int position = 0;
          position = digitalRead(event_buffer[i].reed_pin);  
          boolean triggered = position == event_buffer[i].trigger_state;
          
          if (triggered) {
            set_motor_speed(event_buffer[i].motor, event_buffer[i].speed);
    
            // Set todo to false so this buffer slot can be reused
            event_buffer[i].todo = false;
          }
        } else { // If there is no reed pin event, just set the  motor speed
          set_motor_speed(event_buffer[i].motor, event_buffer[i].speed);
    
          // Set todo to false so this buffer slot can be reused
          event_buffer[i].todo = false;
        }
      }
    }
  }
}

void setup() { 
  SDPsetup();
  
  // Set input and output pins
  pinMode(boardLED, OUTPUT);
  pinMode(reedPin, INPUT);
  digitalWrite(reedPin, HIGH); // Activate internal pullup resistor
  pinMode(prepareReedPin, INPUT);
  digitalWrite(prepareReedPin, HIGH); // Activate internal pullup resistor
  
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
int sensor_read_count = 0;
int sensor_read_interval = 20000;
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
  
  if (sensor_read_count == sensor_read_interval) {
    // The time has come to read values from the sensors and process them as required
    handle_closed_catcher_sensor();
    sensor_read_count = 0;
  }
  sensor_read_count++;

  scomm.readSerial();
    
  event_loop::process_list();
}

void handle_closed_catcher_sensor() {
  int position = 0;
  position = digitalRead(reedPin);  
  boolean closed = position == LOW;
  position = digitalRead(prepareReedPin);  
  boolean prepared = position == LOW;
  
  if (!kicker_running) {
    // Todo: tidy dupicated code
    if (kicker_position == "open" && (closed || prepared)) {
      event_loop::add_command_head(kicker, 100, millis());
      event_loop::add_command_head(kicker, 0, millis()+1000); 
    } else if (kicker_position == "closed" && !closed) {
      event_loop::add_command_head(kicker, -1 * 100, millis());
      event_loop::add_command_pin_trigger(kicker, 0, reedPin, LOW, -1);
    } else if (kicker_position == "prepared" && !prepared) {
      event_loop::add_command_head(kicker, 100, millis());
      event_loop::add_command_head(kicker, PREPARE_SPEED, millis()+750);
      event_loop::add_command_pin_trigger(kicker, 0, prepareReedPin, LOW, millis()+750);
    }
  } else {
    // This handles the strange case if the kicker goes past the catch target and therefore reaches the closed part
    if (kicker_position == "prepared" && closed) {
      set_motor_speed(kicker, 0);
      event_loop::add_command_head(kicker, 100, millis());
      event_loop::add_command_head(kicker, PREPARE_SPEED, millis()+750);
      event_loop::add_command_pin_trigger(kicker, 0, prepareReedPin, LOW, millis()+750);
    } 
  }
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
  
  event_loop::add_command_head(kicker, 100, millis());
  event_loop::add_command_head(kicker, PREPARE_SPEED, millis()+750);
  event_loop::add_command_pin_trigger(kicker, 0, prepareReedPin, LOW, millis()+750);
  
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
  
  event_loop::add_command_head(kicker, -1 * speed, millis());
  event_loop::add_command_pin_trigger(kicker, 0, reedPin, LOW, -1);
  
  kicker_position = "closed";
}

void set_motor_speed(int motor, int speed) {
  // Update whether the kicker is running or not
  if (motor == kicker) {
    if (speed == 0) {
      kicker_running = false;
    } else {
      kicker_running = true;
    }
  }
  
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
