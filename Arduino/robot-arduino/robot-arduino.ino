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

SerialCommand scomm;

int blink = 1;

namespace event_loop {
  typedef struct command_entry {
    int motor;
    int speed;
    unsigned long start_time;
  
    struct command_entry *next;
  } command_entry_t;
  
  void add_command(command_entry_t **head, int motor, int speed, unsigned long start_time)
  {
    // Add the command to the start of the list for simplicity sake
    command_entry_t *new_entry;
    new_entry = (command_entry_t *) malloc(sizeof(command_entry_t));
  
    new_entry->motor = motor;
    new_entry->speed = speed;
    new_entry->start_time = start_time;
    new_entry->next = *head;
    *head = new_entry;
  }
  
  void remove_command(command_entry_t **head, int n)
  {
    command_entry_t *current = *head;
    command_entry_t *temp = NULL;
  
    if (n == 0)
    {
      temp = (*head)->next;
      free(*head);
      *head = temp;
      return;
    }
  
    int i;
    for (i = 0; i < n-1; i++)
    {
      if (current->next != NULL)
      {
        current = current->next;
      }
    }
  
    temp = current->next;
    current->next = temp->next;
    free(temp);
  } 
  
  command_entry_t *head = NULL;
  
  void add_command_head(int motor, int speed, unsigned long start_time)
  {
    add_command(&head, motor, speed, start_time); 
  }
  
  void process_list()
  {
    command_entry_t *current = head;
    int i = 0;
    while (current != NULL)
    {
      if (current->start_time <= millis())
      {
        set_motor_speed(current->motor, current->speed);
        remove_command(&head, i);
      }
      
      current = current->next;
      i++;
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
  scomm.addCommand("set", store_motor_action); // args: [motor, speed, delay]
  scomm.addCommand("prepare_catch", prepare_catch); // args: []
  scomm.addCommand("kick", kick); // args: [speed]
  scomm.addCommand("catch", catch_ball); // args: [speed]
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
    
  event_loop::process_list();
}

// Command callback functions
void store_motor_action() {
    Serial.println("ack");
    char *motorarg = scomm.next();
    char *speedarg = scomm.next();
    char *delayarg = scomm.next();

    int motor = atoi(motorarg);
    int speed = atoi(speedarg);
    int delay = atoi(delayarg);
    
    event_loop::add_command_head(motor, speed, millis()+delay);
}

void prepare_catch() {
  Serial.println("ack");
  // Start the kicker immediately, after 1 second stop it and then reverse it at a reduced speed then stop it 200ms after that
  event_loop::add_command_head(kicker, 100, millis());
  event_loop::add_command_head(kicker, 0, millis()+1000);
  event_loop::add_command_head(kicker, -50, millis()+1500);
  event_loop::add_command_head(kicker, 0, millis()+1700);
}

void kick() {
  Serial.println("ack");
  char *speedarg = scomm.next();
  
  int speed = atoi(speedarg);
  event_loop::add_command_head(kicker, speed, millis());
  event_loop::add_command_head(kicker, 0, millis()+1000);
}

void catch_ball() {
  Serial.println("ack");
  char *speedarg = scomm.next();
  
  int speed = atoi(speedarg);
  
  // Start the catch immediately, after 1 second stop the motor
  event_loop::add_command_head(kicker, -1 * speed, millis());
  event_loop::add_command_head(kicker, 0, millis()+1000);
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
