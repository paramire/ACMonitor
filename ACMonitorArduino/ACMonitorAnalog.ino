#include <SPI.h>
#include <Ethernet.h>

// V0.2
// Enter a MAC address for your controller below.
// Newer Ethernet shields have a MAC address printed on a sticker on the shield
// Older Shield make your own
byte mac[] = { 0xA8, 0x16, 0xB2, 0xFA, 0xAF, 0xD5 };

//Google
//byte server[] = {64,233,187,99};
//IPAddress server(63,233,287,99);

//Flask
//IPAddress server(10,200,253,83);
//byte server[] = {10,200,253,83};

//Juguemos.cl
IPAddress server(107,170,182,27);
//byte server[] = {107,170,182,27};

//Static IP for Arduino
//IPAddress ip(10,200,253,100);
//byte ip[] = {10,200,253,100};

// Initialize the Ethernet client library
// with the IP address and port of the server 
// that you want to connect to (port 80 is default for HTTP):
EthernetServer server(80);

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  Serial.println("Initializing...");
  delay(1000);
  // start the Ethernet connection:
  if(Ethernet.begin(mac)==1){
    Serial.print("OK - ");
    //Print DHCP - IP
    ip = Ethernet.localIP();
    for (byte thisByte = 0; thisByte < 4; thisByte++) {
      // print the value of each byte of the IP address:
      Serial.print(ip[thisByte], DEC);
      Serial.print(".");
    }
  }
  else{
    Serial.println("ERROR"); 
  }
  Serial.println();
  server.begin();
  // give the Ethernet shield a second to initialize:
  delay(2000);
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
          client.println("Refresh: 5");  // refresh the page automatically every 5 sec
          client.println();
          client.println("<!DOCTYPE HTML>");
          client.println("<html>");
          // output the value of each analog input pin
          for (int analogChannel = 0; analogChannel < 6; analogChannel++) {
            int sensorReading = analogRead(analogChannel);
            client.print("analog input ");
            client.print(analogChannel);
            client.print(" is ");
            client.print(sensorReading);
            client.println("<br />");
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