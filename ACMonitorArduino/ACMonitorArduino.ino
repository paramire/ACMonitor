#include <SPI.h>
#include <Ethernet.h>
#include <CS_MQ7.h>
#include "DHT.h"

//CONSTRAITS
#define DHTPIN 2        // PIN 2
#define DHTTYPE DHT11   // DHT 11 
#define MQ7PIN 7        // PIN 7

//MAC
byte mac[] = { 0xA8, 0x16, 0xB2, 0xFA, 0xAF, 0xD5 };

//Google
//byte server[] = {64,233,187,99};
//IPAddress server(63,233,287,99);

//Flask
//IPAddress server(10,200,253,83);
//byte server[] = {10,200,253,83};

//Static IP for Arduino
IPAddress ip(10,200,114,81);
//byte ip[] = {10,200,114,81};

// Initialize the Ethernet client library
// with the IP address and port of the server 
// that you want to connect to (port 80 is default for HTTP):
EthernetServer server(80);

//Variables
DHT dht(DHTPIN, DHTTYPE);     //Object DHT11
CS_MQ7 MQ7(MQ7PIN);           //Object MQ7
int coSensorOutput = 1        //Analog Output
int coData = 0                //Analog Data 

//MQ-7 functions with 1.4V and 5V, when it's functioning with
//5V can't make lectures because the sensor is heating, the library
//and the broker manage, we save the last lecture
int getCO(){
  if(MQ7.currentState() == LOW){
    coData = analogRead(coSensorOutput);
    return coData;
  }
  else{
    return coData;
  }
}

void firstReadCO(){
  if(MQ7.currentState() == LOW){
    coData = analogRead(coSensorOutput);
  }
  else{
    coData = 0;
  }
}


void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  Serial.print("Initializing DHT11...");
  dht.begin();
  Serial.println("- OK");
  delay(1000);
  // start the Ethernet connection:
  Serial.print("Connecting...");
  if(Ethernet.begin(mac)==1){
    Serial.println(" - OK");
    Serial.print("IP: ");
    //Print DHCP - IP
    ip = Ethernet.localIP();
    for (byte thisByte = 0; thisByte < 4; thisByte++) {
      // print the value of each byte of the IP address:
      Serial.print(ip[thisByte], DEC);
      Serial.print(".");
    }
    Serial.println(" - OK");
  }
  else{
    Serial.println(" - ERROR"); 
  }
  //Start Server
  Serial.print("Initializing Server...");
  server.begin();
  Serial.println("- OK");
  delay(2000);
  firstReadCO();
}

void loop()
{
  EthernetClient client = server.available();
  if (client) {
    Serial.println("new client");
    // an http request ends with a blank line
    boolean currentLineIsBlank = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        // if you've gotten to the end of the line (received a newline
        // character) and the line is blank, the http request has ended,
        // so you can send a reply
        if (c == '\n' && currentLineIsBlank) {
          // send a standard http response header
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/html");
          client.println("Connection: close");  // the connection will be closed after completion of the response
          client.println("Refresh: 10");  // refresh the page automatically every 5 sec
          client.println();
          client.println("<!DOCTYPE HTML>");
          client.println("<html>");
          
          float hum = dht.readHumidity();
          float tem = dht.readTemperature();

          if(isnan(hum) || isnan(tem)){
            client.print("<h1>Failed to read Temperature/Humidity</h1>");
          }
          else{
            client.print("<h1>Temperature ");
            client.print(tem);
            client.print("</h1><br />");
            client.print("<h1>Humidity ");
            client.print(hum);
            client.println("</h1><br/>");
            client.print("<h1>CO_2 ");
            client.print(getCO());
            client.println("</h1><br/>");
          }
          client.println("</html>");
          break;
        }
        if (c == '\n') {
          // you're starting a new line
          currentLineIsBlank = true;
        }
        else if (c != '\r') {
          // you've gotten a character on the current line
          currentLineIsBlank = false;
        }
      }
    }
    // give the web browser time to receive the data
    delay(1);
    // close the connection:
    client.stop();
    Serial.println("client disconnected");
  }
}