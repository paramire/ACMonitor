#include <SPI.h>
#include <Ethernet.h>

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
EthernetClient client;

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
  // give the Ethernet shield a second to initialize:
  delay(2000);

  Serial.println("connecting...");
  // if you get a connection, report back via serial:
  if (client.connect(server, 80)) {
    Serial.println("connected");
    // Make a HTTP request:
    client.println("GET / HTTP/1.1");
    client.println("Host: www.juguemos.cl");
    client.println("Connection: close");
    client.println();
  } 
  else {
    // kf you didn't get a connection to the server:
    Serial.println("connection failed");
  }
}

void loop()
{
  // if there are incoming bytes available 
  // from the server, read them and print them:
  if (client.available()) {
    char c = client.read();
    Serial.print(c);
  }

  // if the server's disconnected, stop the client:
  if (!client.connected()) {
    Serial.println();
    Serial.println("disconnecting.");
    client.stop();

    // do nothing forevermore:
    while(true);
  }
}