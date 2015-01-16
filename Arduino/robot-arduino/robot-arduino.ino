
byte maxCommandLength = 20;
char command[20]; // This will hold the command we recieve from the PC
byte index = 0; // This is the index for the command array we use when reading from the serial

void setup()
{
  pinMode(13, OUTPUT);   // initialize pin 13 as digital output (LED)
  pinMode(8, OUTPUT);    // initialize pin 8 to control the radio
  digitalWrite(8, HIGH); // select the radio
  Serial.begin(115200);    // start the serial port at 115200 baud (correct for XinoRF and RFu, if using XRF + Arduino you might need 9600)
  
  Serial.println("power_on");
}

void loop() {
  byte commandResult = getCommand();
  if (commandResult == 1) {
    Serial.println(command);
  } else if (commandResult == 2) {
    Serial.println("command_buffer_full"); 
  }
}
  
byte getCommand()
{
  while (Serial.available()>=1) // character received
  {
    if (index < (maxCommandLength-1)) {
      command[index] = Serial.read();
      if (command[index] == '\r') {
        command[index] = '\0';
        index = 0;
        return 1;
      } else {
        index++;
      }
      
    } else {
      index = 0;
      command[0] = '\0'; // Empty the command buffer
      return 2; // Complain that the command buffer is full 
    }
  }
}

