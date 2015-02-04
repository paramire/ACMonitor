#include <Streaming.h>         // Include the Streaming library
#include <Ethernet.h>          // Include the Ethernet library
#include <SPI.h>
#include <MemoryFree.h>
#include <Agentuino.h> 
#include <Flash.h>
#include <CS_MQ7.h>
#include "DHT.h"

#define DHTPIN 2
#define DHTTYPE DHT11
#define MQ7PIN 7
//
#define DEBUG
//
static byte mac[] = { 0xA8, 0x16, 0xB2, 0xFA, 0xAF, 0xD5 };
static byte ip[] = { 10, 200, 114, 81 };
//
// tkmib - linux mib browser
//
// RFC1213-MIB OIDs
// .iso (.1)
// .iso.org (.1.3)
// .iso.org.dod (.1.3.6)
// .iso.org.dod.internet (.1.3.6.1)
// .iso.org.dod.internet.mgmt (.1.3.6.1.2)
// .iso.org.dod.internet.mgmt.mib-2 (.1.3.6.1.2.1)
// .iso.org.dod.internet.mgmt.mib-2.system (.1.3.6.1.2.1.1)
// .iso.org.dod.internet.mgmt.mib-2.system.sysDescr (.1.3.6.1.2.1.1.1)
static const char sysDescr[] PROGMEM      = "1.3.6.1.2.1.1.1.0";  // read-only  (DisplayString)
// .iso.org.dod.internet.mgmt.mib-2.system.sysObjectID (.1.3.6.1.2.1.1.2)
static const char sysObjectID[] PROGMEM   = "1.3.6.1.2.1.1.2.0";  // read-only  (ObjectIdentifier)
// .iso.org.dod.internet.mgmt.mib-2.system.sysUpTime (.1.3.6.1.2.1.1.3)
static const char sysUpTime[] PROGMEM     = "1.3.6.1.2.1.1.3.0";  // read-only  (TimeTicks)
// .iso.org.dod.internet.mgmt.mib-2.system.sysContact (.1.3.6.1.2.1.1.4)
static const char sysContact[] PROGMEM    = "1.3.6.1.2.1.1.4.0";  // read-write (DisplayString)
// .iso.org.dod.internet.mgmt.mib-2.system.sysName (.1.3.6.1.2.1.1.5)
static const char sysName[] PROGMEM       = "1.3.6.1.2.1.1.5.0";  // read-write (DisplayString)
// .iso.org.dod.internet.mgmt.mib-2.system.sysLocation (.1.3.6.1.2.1.1.6)
static const char sysLocation[] PROGMEM   = "1.3.6.1.2.1.1.6.0";  // read-write (DisplayString)
// .iso.org.dod.internet.mgmt.mib-2.system.sysServices (.1.3.6.1.2.1.1.7)
static const char sysServices[] PROGMEM   = "1.3.6.1.2.1.1.7.0";  // read-only  (Integer)
//TEMP HUMD CO
static const char sysTemp[] PROGMEM   = "1.3.6.1.4.1.36582.1.1.0";  // read-only  (Integer)
static const char sysHumd[] PROGMEM   = "1.3.6.1.4.1.36582.1.2.0";  // read-only  (Integer)
static const char sysCO[] PROGMEM     = "1.3.6.1.4.1.36582.1.3.0";  // read-only  (Integer)
//
// Arduino defined OIDs
// .iso.org.dod.internet.private (.1.3.6.1.4)
// .iso.org.dod.internet.private.enterprises (.1.3.6.1.4.1)
// .iso.org.dod.internet.private.enterprises.arduino (.1.3.6.1.4.1.36582)
//
//
// RFC1213 local values
static char locDescr[]              = "A/C Monitor ALMA";                       // read-only (static)
static uint32_t locUpTime           = 0;                                        // read-only (static)
static char locContact[20]          = "ALMA";                                   // should be stored/read from EEPROM - read/write (not done for simplicity)
static char locName[20]             = "Agentuino";                              // should be stored/read from EEPROM - read/write (not done for simplicity)
static char locLocation[20]         = "Santiago, CH";                           // should be stored/read from EEPROM - read/write (not done for simplicity)
static int32_t locServices          = 7;                                        // read-only (static)
static int32_t locTemp              = 0;                                        // read-only (static)
static int32_t locHumd              = 0;                                        // read-only (static)
static int32_t locCO                = 0;                                        // read-only (static)

uint32_t prevMillis = millis();
char oid[SNMP_MAX_OID_LEN];
SNMP_API_STAT_CODES api_status;
SNMP_ERR_CODES status;

//SENSOR VARIABLES
DHT dht(DHTPIN, DHTTYPE);     //Object DHT11
CS_MQ7 MQ7(MQ7PIN);           //Object MQ7
int coSensorOutput = 1;        //Analog Output

void pduReceived()
{
  SNMP_PDU pdu;
  //
  #ifdef DEBUG
    Serial << F("UDP Packet Received Start..") << F(" RAM:") << freeMemory() << endl;
  #endif
  //
  api_status = Agentuino.requestPdu(&pdu);
  //
  if( pdu.type == SNMP_PDU_GET || pdu.type == SNMP_PDU_GET_NEXT || pdu.type == SNMP_PDU_SET
    && pdu.error == SNMP_ERR_NO_ERROR && api_status == SNMP_API_STAT_SUCCESS){

    pdu.OID.toString(oid);
    //
    //Serial << "OID: " << oid << endl;
    //
    if(strcmp_P(oid, sysDescr) == 0){
      // handle sysDescr (set/get) requests
      if(pdu.type == SNMP_PDU_SET){
        // response packet from set-request - object is read-only
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = SNMP_ERR_READ_ONLY;
      }
      else{
        // response packet from get-request - locDescr
        status = pdu.VALUE.encode(SNMP_SYNTAX_OCTETS, locDescr);
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;
      }
      //
      #ifdef DEBUG
        Serial << F("sysDescr...") << locDescr << F(" ") << pdu.VALUE.size << endl;
      #endif
    }
    else if(strcmp_P(oid, sysUpTime ) == 0){
      // handle sysName (set/get) requests
      if(pdu.type == SNMP_PDU_SET){
        // response packet from set-request - object is read-only
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = SNMP_ERR_READ_ONLY;
      }
      else{
        // response packet from get-request - locUpTime
        status = pdu.VALUE.encode(SNMP_SYNTAX_TIME_TICKS, locUpTime);
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;
      }
      //
      #ifdef DEBUG
        Serial << F("sysUpTime...") << locUpTime << F(" ") << pdu.VALUE.size << endl;
      #endif
    } 
    else if(strcmp_P(oid, sysName ) == 0){
      // handle sysName (set/get) requests
      if(pdu.type == SNMP_PDU_SET){
        // response packet from set-request - object is read/write
        status = pdu.VALUE.decode(locName, strlen(locName)); 
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;
      }
      else {
        // response packet from get-request - locName
        status = pdu.VALUE.encode(SNMP_SYNTAX_OCTETS, locName);
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;
      }
      //
      #ifdef DEBUG
        Serial << F("sysName...") << locName << F(" ") << pdu.VALUE.size << endl;
      #endif
    }
    else if(strcmp_P(oid, sysContact ) == 0){
      // handle sysContact (set/get) requests
      if(pdu.type == SNMP_PDU_SET){
        // response packet from set-request - object is read/write
        status = pdu.VALUE.decode(locContact, strlen(locContact)); 
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;
      }
      else{
        // response packet from get-request - locContact
        status = pdu.VALUE.encode(SNMP_SYNTAX_OCTETS, locContact);
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;
      }
      //
      #ifdef DEBUG
        Serial << F("sysContact...") << locContact << F(" ") << pdu.VALUE.size << endl;
      #endif
    }
    else if(strcmp_P(oid, sysLocation ) == 0){
      // handle sysLocation (set/get) requests
      if(pdu.type == SNMP_PDU_SET){
        // response packet from set-request - object is read/write
        status = pdu.VALUE.decode(locLocation, strlen(locLocation)); 
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;
      }
      else{
        // response packet from get-request - locLocation
        status = pdu.VALUE.encode(SNMP_SYNTAX_OCTETS, locLocation);
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;
      }
      //
      #ifdef DEBUG
        Serial << F("sysLocation...") << locLocation << F(" ") << pdu.VALUE.size << endl;
      #endif
    }
    else if(strcmp_P(oid, sysServices) == 0){
      // handle sysServices (set/get) requests
      if(pdu.type == SNMP_PDU_SET){
        // response packet from set-request - object is read-only
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = SNMP_ERR_READ_ONLY;
      }
      else{
        // response packet from get-request - locServices
        status = pdu.VALUE.encode(SNMP_SYNTAX_INT, locServices);
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;
      }
      #ifdef DEBUG
        Serial << F("locServices...") << locServices << F(" ") << pdu.VALUE.size << endl;
      #endif
    }
    else if(strcmp_P(oid, sysTemp) == 0){
      //SEND TEMP
      if(pdu.type == SNMP_PDU_SET){
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = SNMP_ERR_READ_ONLY;
      }
      else{
        status = pdu.VALUE.encode(SNMP_SYNTAX_INT, locTemp);
        //status = pdu.VALUE.encode(SNMP_SYNTAX_OCTETS, locTemp);
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;        
      }
    }
    else if(strcmp_P(oid, sysHumd) == 0){
      //SEND HUMD
      if(pdu.type == SNMP_PDU_SET){
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = SNMP_ERR_READ_ONLY;
      }
      else{
        //status = pdu.VALUE.encode(SNMP_SYNTAX_OCTETS, locHumd);
        status = pdu.VALUE.encode(SNMP_SYNTAX_INT, locHumd);
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;
      }
    }
    else if(strcmp_P(oid, sysCO) == 0){
      //SEND CO
      if(pdu.type == SNMP_PDU_SET){
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = SNMP_ERR_READ_ONLY;
      }
      else{
        status = pdu.VALUE.encode(SNMP_SYNTAX_INT, locCO);
        //status = pdu.VALUE.encode(SNMP_SYNTAX_OCTETS, locContact);
        pdu.type = SNMP_PDU_RESPONSE;
        pdu.error = status;
      }
    }
    else {
      // oid does not exist
      // response packet - object not found
      pdu.type = SNMP_PDU_RESPONSE;
      pdu.error = SNMP_ERR_NO_SUCH_NAME;
    }
    Agentuino.responsePdu(&pdu);
  }
  Agentuino.freePdu(&pdu);
  //Serial << "UDP Packet Received End.." << " RAM:" << freeMemory() << endl;
}

int getCO(){
  if(MQ7.currentState() == LOW){
    locCO = analogRead(coSensorOutput);
    return locCO;
  }
  else
    return locCO;
}

void firstReadCO(){
  if(MQ7.currentState() == LOW)
    //coData = analogRead(coSensorOutput);
    locCO = analogRead(coSensorOutput);
  else
    locCO = 0;
}

void setup()
{
  Serial.begin(9600);
  Ethernet.begin(mac);
  dht.begin();
  firstReadCO();
  api_status = Agentuino.begin();

  if ( api_status == SNMP_API_STAT_SUCCESS ) {
    Agentuino.onPduReceive(pduReceived);
    delay(10);
    Serial << F("SNMP Agent Initalized...") << endl;
    return;
  }
  delay(10);
  Serial << F("SNMP Agent Initalization Problem...") << status << endl;
}

void loop(){
  MQ7.CoPwrCycler();
  // listen/handle for incoming SNMP requests
  Agentuino.listen();
  // sysUpTime - The time (in hundredths of a second) since
  // the network management portion of the system was last
  // re-initialized.
  if(millis() - prevMillis > 1000){
    // increment previous milliseconds
    prevMillis += 1000;
    // increment up-time counter
    locUpTime += 100;
    
    locHumd = (int) dht.readHumidity();
    locTemp = (int) dht.readTemperature();
    getCO();
  }
}