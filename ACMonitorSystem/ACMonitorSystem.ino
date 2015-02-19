#include <SPI.h>
#include <XBee.h>
#include <Time.h>

#define TIME_MSG_LEN  11   // time sync to PC is HEADER followed by Unix time_t as ten ASCII digits
#define TIME_HEADER  'T'   // Header tag for serial time sync message
#define TIME_REQUEST  7    // ASCII bell character requests a time sync message
#define THRESHOLD 0
//********************************
//FLAG XBEE
#define TIME_FLAG 0x0F
#define KEEP_ALIVE_FLAG 0x21
#define ALARM_FLAG 0x55
#define AlARM_ON_FLAG 0x56
#define FINISH_FLAG 0xAA
#define ERROR_FLAG 0xFF
//********************************
//Pin preparation
uint8_t ssRX = 1;
uint8_t ssTX = 2;
uint8_t ain0 = 6;
uint8_t ain1 = 7;
static const uint8_t aPin1 = 1;
static const uint8_t aPin2 = 2;
static const uint8_t aPin3 = 3;
static const uint8_t aPin4 = 4;
//********************************
//XBee Preparation
XBee xbee = XBee();
XBeeAddress64 addr64  = XBeeAddress64();
//Time Message
uint8_t payloadTime[]    = {0};
ZBTxRequest zbTxTime     = ZBTxRequest(addr64,payloadTime,sizeof(payloadTime));
//Alarm Message
uint8_t payloadAlarm[]   = {0,0,0,0,0};
ZBTxRequest zbTxAlarm    = ZBTxRequest(addr64,payloadAlarm,sizeof(payloadAlarm));
//Alarm ON Message
uint8_t payloadAlarmOn[] = {0,0,0,0,0,0,0,0,0,0};
ZBTxRequest zbTxAlarmOn  = ZBTxRequest(addr64,payloadAlarmOn,sizeof(payloadAlarmOn));
//Keep Alive Message
uint8_t payloadAlive[]   = {0};
ZBTxRequest zbTxAlive    = ZBTxRequest(addr64,payloadAlive,sizeof(payloadAlive));
//Finish Message
uint8_t payloadFinish[]  = {0,0,0,0,0};
ZBTxRequest zbTxFinish   = ZBTxRequest(addr64,payloadFinish,sizeof(payloadFinish));
//********************************
//XBee Response
ZBTxStatusResponse txStatus = ZBTxStatusResponse();
ZBRxResponse rx = ZBRxResponse();
ModemStatusResponse msr = ModemStatusResponse();
//*******************************
//Alarm output
uint16_t alarmChiller0 = 0;
uint16_t alarmGeneral0 = 0;
uint16_t alarmChiller1 = 0;
uint16_t alarmGeneral1 = 0;
//*******************************
//Alarm output
uint8_t outputChiller0 = 0;
uint8_t outputGeneral0 = 0;
uint8_t outputChiller1 = 0;
uint8_t outputGeneral1 = 0;
//*********************************
//Function interrupt when it recive
//a ADC value
int messageTime;
time_t currentTime;
time_t stillAliveTime;
volatile boolean trigger = false;
volatile boolean trigger_alarm = false;

ISR(ANALOG_COMP_vect){
	trigger_alarm=true;
}

/*-------------------------------------
VOID intToChar(int value, char b)

int value = Value to Transform
char b    = Reference to char array

Simple transform a int Value in 
a Char Array (String)

Return: NONE
-------------------------------------*/
void intToChar(int value, char *b){
  String aux;
  char a[10];
  aux = String(value);
  aux.toCharArray(a,10);
  strcpy(b,"T");
  strcat(b,a);
}
/*-------------------------------------
VOID processTimeMessage(char *timeMSG)

char *timeMSG    = Char array, consist
in header ('T') and 10 ASCII digits

Set the internal clock of the Arduino
to the 'timeMSG' value


Return: NONE
-------------------------------------*/
void processTimeMessage(char* timeMSG) {
	char c = timeMSG[0];  
	if(c == TIME_HEADER){      
	  time_t pctime = 0;
	  for(int i=1; i < TIME_MSG_LEN -1; i++){  
	    c = timeMSG[i];          
	    // convert digits to a number
	    if( c >= '0' && c <= '9')
	      	pctime = (10 * pctime) + (c - '0');   
	  }
	  // Sync Arduino clock to the time received on the serial port  
	  setTime(pctime);   
	}
}
/*-------------------------------------
VOID sendTimeRequest()

Send a TIME packet, and wait for a response


return: None
-------------------------------------*/
void sendTimeRequest(){
	payloadTime[0] = TIME_FLAG;
	xbee.send(zbTxTime);
	//MEJORA DEFINIR UN TIEMPO DE INICIO Y UN MAXIMO
	//Espero que me envien la respuesta para procesarla
	char datetime[11];
	int fin = 0;
	boolean time_set = true;
	while(time_set){
		xbee.send(zbTxTime);
		if(millis() < 300000){
			if (xbee.readPacket(500)) {
				if(xbee.getResponse().isAvailable()){
					if(xbee.getResponse().getApiId() == ZB_RX_RESPONSE){
						//XBee SEND MESSAGE
						xbee.getResponse().getZBRxResponse(rx);
						if(rx.getOption() == ZB_PACKET_ACKNOWLEDGED){
							//OBTENER LA HORA
							//Cada 8 bit
							for(int i = 0; i < rx.getDataLength();i++){
								fin = (fin | rx.getData(i)) << 8;
							}
							time_set = false;
							intToChar(fin,datetime);
							processTimeMessage(datetime);
						}
					}
					else if(xbee.getResponse().getApiId() == MODEM_STATUS_RESPONSE){
					    //XBee Modem Message
					    xbee.getResponse().getModemStatusResponse(msr);
					    if(msr.getStatus() == ASSOCIATED){
					    	Serial.println("MODEM_ASSOCIATED");
					    }
					    else if(msr.getStatus() == DISASSOCIATED){
					    	Serial.println("MODEM_DISASSOCIATED");
					    }
					}
				}
				else if(xbee.getResponse().isError()){
					Serial.print("ERROR: ");
					Serial.println(xbee.getResponse().getErrorCode());
				}
			}
			delay(1000);
		}
		else{
			time_set = false;
		}
	}
}
/*-------------------------------------
BOOLEAN sendAlarm()

Send a XBee packet with a ALARM PACKET
until that the coordinator recieve the 
message and receive a response TX_STATUS 

return: TRUE
-------------------------------------*/
boolean sendAlarm(){
	//ALARM_FLAG
	payloadAlarm[0] = ALARM_FLAG; 
	//Prepare the Time DATA
	currentTime = now();
	payloadAlarm[1] = currentTime >> 24 & 0xff;
	payloadAlarm[2] = currentTime >> 16 & 0xff;
	payloadAlarm[3] = currentTime >> 8 & 0xff;
	payloadAlarm[4] = currentTime & 0xff;

 	while(trigger){
 		xbee.send(zbTxAlarm);
 		//wait until receive a TX_STATUS response
 		if (xbee.readPacket(500)){
		    if (xbee.getResponse().getApiId() == ZB_TX_STATUS_RESPONSE) {
		      	xbee.getResponse().getZBTxStatusResponse(txStatus);
		      	//Check if it succefull
		      	if (txStatus.getDeliveryStatus() == SUCCESS)
		      		trigger = false;
		    }
		}
		delay(1000);
	}
	return true;
}
/*-------------------------------------
VOID sendAlarmOn()

Send a Zigbee/XBee packet with a ALARM ON
PACKET wich contain
Byte 0 - FLAG
Byte 1 - TIME 1
Byte 2 - TIME 2
Byte 3 - TIME 3
Byte 4 - TIME 4
Byte 5 - THRESHOLD
Byte 6 - ALARM 1
Byte 7 - ALARM 2
Byte 8 - ALARM 3
Byte 9 - ALARM 4
Don't wait TX_STATUS Response

return: None
-------------------------------------*/
void sendAlarmOn(){
	//Check the status of the alarm
	alarmChiller0 = analogRead(A1);
	alarmGeneral0 = analogRead(A2);
	alarmChiller1 = analogRead(A3);
	alarmGeneral1 = analogRead(A4);
	//Map the Input Value (0-1023  to scale 0 - 255)
	outputChiller0 =  map(alarmChiller0,0,1023,0,255);
	outputGeneral0 =  map(alarmGeneral0,0,1023,0,255);
	outputChiller1 =  map(alarmChiller1,0,1023,0,255);
	outputGeneral1 =  map(alarmGeneral1,0,1023,0,255);
	//Alarm_On FLAG
	payloadAlarmOn[0] = STATUS_FLAG;
	//Alarm_On TIME
	payloadAlarmOn[1] = STATUS_FLAG;
	payloadAlarmOn[2] = STATUS_FLAG;
	payloadAlarmOn[3] = STATUS_FLAG;
	payloadAlarmOn[4] = STATUS_FLAG;
	//Alarm_On THRESHOLD
	payloadAlarmOn[5] = THRESHOLD;
	//Alarm_On INFO
 	payloadAlarmOn[6] = outputChiller0 & 0xff; 
	payloadAlarmOn[7] = outputGeneral0 & 0xff;
	payloadAlarmOn[8] = outputChiller1 & 0xff;
	payloadAlarmOn[9] = outputGeneral1 & 0xff;
	//Send Message
	xbee.send(zbTxAlarmOn);
}
/*-------------------------------------
VOID sendKeepAlive()

Send a Zigbee/XBee packet with a 
KEEP ALIVE PACKET wich contain
Byte 0 - FLAG
Don't wait TX_STATUS Response

return: None
-------------------------------------*/

void sendKeepAlive(){
	//Still Alive FLAG
	payloadAlive[0] = KEEP_ALIVE_FLAG;
	xbee.send(zbTxKeepAlive);
}
/*-------------------------------------
VOID sendFinish()

Send a FINISH Packet 
Byte 0 - FLAG
Byte 1 - TIME 1
Byte 2 - TIME 2
Byte 3 - TIME 3
Byte 4 - TIME 4
Don't wait TX_STATUS Response

return: None
-------------------------------------*/
void sendFinish(){
	currentTime = now();
	payloadFinish[0] = FINISH_FLAG;
	payloadFinish[1] = currentTime >> 24 & 0xFF;
	payloadFinish[2] = currentTime >> 16 & 0xFF;
	payloadFinish[3] = currentTime >> 8 & 0xFF;
	payloadFinish[4] = currentTime & 0xFF;
	xbee.send(zbTxFinish)
}
/*-------------------------------------
BOOLEAN status()

Check if ALL Analog Inputs are behind 
the THRESHOLD, 
return: TRUE, if below THRESHOLD
return: FALSE, if above THRESHOLD
-------------------------------------*/
boolean status(){
	alarmChiller0 = analogRead(A1);
	alarmGeneral0 = analogRead(A2);
	alarmChiller1 = analogRead(A3);
	alarmGeneral1 = analogRead(A4);	
	//Si todas las alarmas apagadas, dejamos de enviar mensajes
	if((alarmChiller0 <= THRESHOLD) && (alarmGeneral0 <= THRESHOLD) && (alarmChiller1 <= THRESHOLD) && (alarmGeneral1 <= THRESHOLD) ){
		//trigger_alarm = false;
		return false;
	}
	return true;
}
/*-------------------------------------
VOID setup()

Main function Arduino
- Set XBee/ZigBee
- Set the PINS
- Set Analog Comparator
- Send Time Request

return: None
-------------------------------------*/
void setup(){
	//XBee Initilization
	Serial.begin(9600);
	xbee.begin(Serial);
	//Analog Comparator PIN
	pinMode(ain0,INPUT);
	pinMode(ain1,INPUT);
	//Analog PIN
	pinMode(aPin1,INPUT);
	pinMode(aPin2,INPUT);
	pinMode(aPin3,INPUT);
	pinMode(aPin4,INPUT);

	//Set Analog comparator
	ADCSRB &= ~(1<<ACME);

	ACSR = 	(0<<ACD) | 		// Analog Comparator: Enabled
  			(0<<ACBG) |  	// Analog Comparator Bandgap Select: AIN0 is applied to the positive input
  			(0<<ACO) |   	// only readable
  			(1<<ACI) |   	// Analog Comparator Interrupt Flag: Clear Pending Interrupt
  			(1<<ACIE) |   	// Analog Comparator Interrupt: Enabled
  			(0<<ACIC) |   	// Analog Comparator Input Capture: Disabled
  			(1<<ACIS1) | (1<<ACIS0);  
  	//CAMBIAR A ONLY RISING
  	//Time configuration
  	sendTimeRequest();
  	stillAliveTime = now();
}
/*-------------------------------------
VOID Loop()

Main function Arduino
- Check if Trigger = TRUE
 - IF TRUE send ALARM PACKET
- Check if Trigger_alarm = TRUe
 - IF TRUE send ALARM ON
 - Check status()
- Send Keep Alive packet every 5 Min 
return: None
-------------------------------------*/
void loop(){
	if(trigger){
		//Send Time 
		trigger_alarm = sendAlarm();
	}
	while(trigger_alarm){
 		sendAlarmOn();
 		//Check the Alarm status
		trigger_alarm = status();
		//If the alarm set on meanwhile
		if(trigger_alarm == false){
			sendFinish();
		}
		if(trigger == true){
			trigger_alarm = true;
		}
		delay(1000);
	}
	//Send StillAliveMSG every 5 min
	if(stillAliveTime + 300 > now()){
		stillAliveTime = now();
		sendKeepAlive();
	}
}