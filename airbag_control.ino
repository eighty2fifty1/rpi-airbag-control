//still need to figure out saving EEPROM values
#include <EEPROM.h>
#include <MAX485.h>
#include <SoftwareSerial.h>

//EEPROM placeholders
int lPlace;
int rtPlace;
int eeAddr = 0;

//pin setup
int relay = 5;
int leftFill = 6;
int rtFill = 7;
int leftDump = 8;
int rtDump = 9;
int re = 11;
int de = 11;
int rx = 10;
int tx = 12;
int leftRaw;
int rtRaw;

//pressure variables
int leftSet = 5;
int rtSet = 5;
int leftPress, rtPress;

//serial comm variables
const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];
bool newData = false;
int manualMode = 0;
int manualPump = 0;


// serial comm objects
MAX485 Rs485(re, de);
SoftwareSerial MySerial(rx, tx);

//status message
//(bool) pump relay, left fill, right fill, left dump, right dump,
//(int) left setting, right setting, left pressure reading, right pressure reading
int status[10] = {0, 0, 0, 0, 0, leftSet, rtSet, 0, 0, manualMode};

void setup() {
  //pin settings
  pinMode(relay, OUTPUT);
  pinMode(leftFill, OUTPUT);
  pinMode(rtFill, OUTPUT);
  pinMode(leftDump, OUTPUT);
  pinMode(rtDump, OUTPUT);

  //serial setup

  Serial.begin(19200);        //for debugging, won't be used in normal ops
  MySerial.begin(19200);

  //read previous values off EEPROM
  Serial.println(EEPROM.get(eeAddr, lPlace));
  eeAddr += sizeof(int);
  Serial.println(eeAddr);
  Serial.println(EEPROM.get(eeAddr, rtPlace));


  if ((lPlace > 5) && (lPlace < 90))
    leftSet = lPlace;

  if ((rtPlace > 5) && (rtPlace < 90))
    rtSet = rtPlace;
  status[5] = leftSet;
  status[6] = rtSet;
  //clearEEPROM();
}

void loop() {
  //pressure read
  leftRaw = analogRead(A0);
  rtRaw = analogRead(A1);
  //Serial.println(leftRaw);
  //Serial.println(rtRaw);
  leftPress = pressureConvert(leftRaw);
  rtPress = pressureConvert(rtRaw);
  status[7] = leftPress;
  status[8] = rtPress;
  /*
    Serial.print("Left Sensor Reads: ");
    Serial.println(leftPress);
    Serial.print("Right Sensor Reads: ");
    Serial.println(rtPress);
  */

  //automatic pressure control
  if (manualMode == 0) {
    //Serial.println("auto mode");
    //relays energize when LOW signal (grounded out)
    //fill left
    if (leftPress < (leftSet - 2)) {
      digitalWrite(relay, LOW);
      status[0] = 1;
      digitalWrite(leftFill, LOW);
      status[1] = 1;
      digitalWrite(leftDump, HIGH);
      status[3] = 0;
      //Serial.println("Left airbag filling");
    }

    //dump left
    else if (leftPress > (leftSet + 2)) {
      digitalWrite(leftDump, LOW);
      status[3] = 1;
      digitalWrite(leftFill, HIGH);
      status[1] = 0;
      //Serial.println("Left airbag dumping");
    }

    //idle
    else {
      digitalWrite(leftDump, HIGH);
      status[3] = 0;
      digitalWrite(leftFill, HIGH);
      status[1] = 0;
    }

    //fill right
    if (rtPress < (rtSet - 2)) {
      digitalWrite(relay, LOW);
      status[0] = 1;
      digitalWrite(rtFill, LOW);
      status[2] = 1;
      digitalWrite(rtDump, HIGH);
      status[4] = 0;
      //Serial.println("Right airbag filling");
    }
    //dump right
    else if (rtPress > (rtSet + 2)) {
      digitalWrite(rtDump, LOW);
      status[4] = 1;
      digitalWrite(rtFill, HIGH);
      status[2] = 0;
      //Serial.println("Right airbag dumping");
    }

    //idle
    else {
      digitalWrite(rtDump, HIGH);
      status[4] = 0;
      digitalWrite(rtFill, HIGH);
      status[2] = 0;
    }
    //turn off pump
    if ((rtPress > rtSet - 2) && (leftPress > leftSet - 2)) {
      digitalWrite(relay, HIGH);
      status[0] = 0;
      //Serial.println("Both pressures high, pump off");
    }
  }

  //manual pump control for filling tires
  else{
    //Serial.println("manual mode");
    //closes all solenoids
    digitalWrite(leftFill, HIGH);
    digitalWrite(leftDump, HIGH);
    digitalWrite(rtFill, HIGH);
    digitalWrite(rtDump,HIGH);
    status[1] = 0;
    status[2] = 0;
    status[3] = 0;
    status[4] = 0;

    //pump on
    if (manualPump == 1){
      digitalWrite(relay, LOW);
      status[0] = 1;
    }
    else{
      digitalWrite(relay, HIGH);
      status[0] = 0;
    }
  }
  MySerial.listen();
  if (MySerial.available()) {
    serialRecv();
  }
  sendUSBStatus();          //for debugging
  sendStatus();
  delay(200);
}
///////////////////////////////////////////////
//                 FUNCTIONS                 //
///////////////////////////////////////////////

//converts analog signal to psi.  requires testing
float pressureConvert(float in) {
  float psi;
  psi = (in / 1023) * 200;
  return psi;
}

//============

void serialRecv() {
  //Serial.println("receive function called");
  recvWithStartEndMarkers();
  if (newData == true) {
    strcpy(tempChars, receivedChars);
    // this temporary copy is necessary to protect the original data
    //   because strtok() used in parseData() replaces the commas with \0
    parseData();
    //showParsedData();
    newData = false;
  }
}

//============

void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;
  //Serial.println("other recv fucntion called");
  while (MySerial.available() > 0 && newData == false) {
    //Serial.println("data found");
    rc = MySerial.read();
    //Serial.print(rc);

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      }
      else {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }

    else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

//============

void parseData() {      // split the data into its parts
  eeAddr = 0;
  char * strtokIndx; // this is used by strtok() as an index

  strtokIndx = strtok(tempChars, ",");     // get the first part - the string
  leftSet = atoi(strtokIndx); // copy it to messageFromPC
  status[5] = leftSet;
  EEPROM.put(eeAddr, leftSet);
  //Serial.println(EEPROM.get(eeAddr, lPlace));
  eeAddr += sizeof(int);
  strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
  rtSet = atoi(strtokIndx);     // convert this part to an integer
  status[6] = rtSet;
  EEPROM.put(eeAddr, rtSet);
  //Serial.println(EEPROM.get(eeAddr, rtPlace));

  strtokIndx = strtok(NULL, ", ");
  manualMode = atoi(strtokIndx);
  status[9] = manualMode;
  strtokIndx = strtok(NULL, ", ");
  manualPump = atoi(strtokIndx);
}

//============

void showParsedData() {
  Serial.print("Left Setting ");
  Serial.println(leftSet);
  Serial.print("Right Setting ");
  Serial.println(rtSet);
  Serial.println(manualMode);
  Serial.println(manualPump);
}

//============

void sendUSBStatus() {
  //sends status message in this order
  //(bool) pump relay, left fill, right fill, left dump, right dump,
  //(int) left setting, right setting, left pressure reading, right pressure reading, auto/man mode
  for (int i = 0 ; i < 10; i++) {
    Serial.print(status[i]);
    Serial.print(", ");
  }
  Serial.println();
}

//============

void sendStatus() {
  //sends status message in this order
  //(bool) pump relay, left fill, right fill, left dump, right dump,
  //(int) left setting, right setting, left pressure reading, right pressure reading, auto/man mode
  Rs485.sending(true);
  MySerial.print("<");
  for (int i = 0 ; i < 10; i++) {
    MySerial.print(status[i]);
    MySerial.print(", ");
  }
  MySerial.println(">");
  Rs485.sending(false);
}

void clearEEPROM() {
  for (int i = 0; i < EEPROM.length(); i++) {
    EEPROM.write(i, 0);
  }
}
