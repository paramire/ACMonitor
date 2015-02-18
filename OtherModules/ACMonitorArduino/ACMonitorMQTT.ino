#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>

#include <CS_MQ7.h>
#include "DHT.h"

#define DHTPIN 2
#define DHTTYPE DHT11
#define MQ7PIN 7

//MAC
byte mac[] = { 0xA8, 0x16, 0xB2, 0xFA, 0xAF, 0xD5 };

//Google
//byte server[] = {64,233,187,99};
//IPAddress server(63,233,287,99);

//Flask PORT 5000
//IPAddress server(10,200,253,193);
//byte server[] = {10,200,253,193};

//Mosquitto PORT 1883
//IPAddress server(10,200,114,193);
byte server[] = {10,200,114,193};

//Static IP for Arduino
IPAddress ip(10,200,114,81);
//byte ip[] = {10,200,114,81};

//Variables
DHT dht(DHTPIN, DHTTYPE);     //Object DHT11
CS_MQ7 MQ7(MQ7PIN);           //Object MQ7
int coSensorOutput = 1;        //Analog Output
int coData = 0;                //Analog Data
char humC[10];
char temC[10];
char coC[10];

EthernetClient ethClient;
PubSubClient client(server, 1883, callback, ethClient);


void callback(char* topic, byte* payload, unsigned int length) {
  // handle message arrived
}

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

void charear(float value, char *b){
  dtostrf(value,4,2,b);
}

void charear(int value, char *b){
  String aux;
  aux = String(value);
  aux.toCharArray(b,10);
}

void setup()
{
  Serial.begin(9600);
  //DHT11
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
    for (byte thisByte = 0; thisByte < 4; thisByte++){
        // print the value of each byte of the IP address:
      Serial.print(ip[thisByte], DEC);
      Serial.print(".");
    }
    Serial.println(" - OK");
  }
  else{
    Serial.println(" - ERROR"); 
  }
  delay(2000);
  firstReadCO();
        
  if(client.connect("arduinoClient","monitor/status",0,0,"Client Disconnected")) {
    Serial.println("YAY");
  }
}

void loop(){
    MQ7.CoPwrCycler();
    delay(5000);
    if(client.connected()){
      client.loop();
      float hum = dht.readHumidity();
      float tem = dht.readTemperature();
      charear(hum,humC);
      charear(tem,temC);
      charear(getCO(),coC);
      client.publish("monitor/humid",humC);
      client.publish("monitor/temp",temC);
      //add retained flag to CO
      //client.publish("monitor/CO",coC);
      if(MQ7.currentState()==LOW){
        Serial.println("LOW");
        client.publish("monitor/CO",coC);
      }
      else{
        Serial.println("HIGH");
        client.publish("monitor/CO",(uint8_t*) coC,strlen(coC),true);
      }
      client.subscribe("inTopic");
    }
    else{
      if(client.connect("arduinoClient","monitor/status",0,0,"Client Disconnected")) {
         Serial.println("YAY - RECONNECT");
       }
    }  
}

