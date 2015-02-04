#include <SPI.h>
#include <XBee.h>
#include <Time.h>

#define TIME_MSG_LEN  11   // time sync to PC is HEADER followed by Unix time_t as ten ASCII digits
#define TIME_HEADER  'T'   // Header tag for serial time sync message
#define TIME_REQUEST  7    // ASCII bell character requests a time sync message
#define THRESHOLD 0
//********************************
//FLAG XBEE
#define TIME_FLAG 0x0f
#define INIT_FLAG 0x55
#define STATUS_FLAG 0x21
#define STILL_ALIVE_FLAG 0x5d
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
uint8_t payloadTime[] = {0};
ZBTxRequest zbTxTime = ZBTxRequest(addr64,payloadTime,sizeof(payloadTime));
//Initial Trigger Message
uint8_t payloadInit[] = {0,0,0,0,0};
ZBTxRequest zbTxInit = ZBTxRequest(addr64,payloadInit,sizeof(payloadInit));
//Status Alarm Message
uint8_t payloadStat[] = {0,0,0,0,0};
ZBTxRequest zbTxStat = ZBTxRequest(addr64,payloadStat,sizeof(payloadStat));
//Still Alive Message
uint8_t payloadAlive[] = {0};
ZBTxRequest zbTxAlive = ZBTxRequest(addr64,payloadAlive,sizeof(payloadAlive));
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
//Int to Char for the Time
void intToChar(int value, char *b){
  String aux;
  char a[10];
  aux = String(value);
  aux.toCharArray(a,10);
  strcpy(b,"T");
  strcat(b,a);
}

void processSyncMessage(char* timeMSG) {
  	// time message consists of header & 10 ASCII digits
	char c = timeMSG[0];  
	if(c == TIME_HEADER){      
	  time_t pctime = 0;
	  for(int i=1; i < TIME_MSG_LEN -1; i++){  
	    c = timeMSG[i];          
	    if( c >= '0' && c <= '9'){
	    	// convert digits to a number
	      	pctime = (10 * pctime) + (c - '0');     
	    }
	  }
	  // Sync Arduino clock to the time received on the serial port  
	  setTime(pctime);   
	}
}

void sendTimeRequest(){
	//Time FLAG - 00001111
	char datetime[11];
	payloadTime[0] = TIME_FLAG;
	xbee.send(zbTxTime);
	int fin = 0;
	//MEJORA DEFINIR UN TIEMPO DE INICIO Y UN MAXIMO
	//Espero que me envien la respuesta para procesarla
	boolean time_set = true;
	while(time_set){
		xbee.send(zbTxTime);
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
						intToChar(fin,datetime);
						processSyncMessage(datetime);
					}
					else{
						//Recibio ZB_BROADCAST_PACKET
						Serial.println("ZB_BROADCAST_PACKET");
					}
				}
				else if(xbee.getResponse().getApiId() == MODEM_STATUS_RESPONSE){
				    //XBee Modem Message
				    xbee.getResponse().getModemStatusResponse(msr);
				    if(msr.getStatus() == ASSOCIATED){
				    	//SABER QUE HACER ACA
				    	Serial.println("MODEM_ASSOCIATED");
				    }
				    else if(msr.getStatus() == DISASSOCIATED){
				    	//ACA TAMBIEN
				    	Serial.println("MODEM_DISASSOCIATED");
				    }
				}
			}
			else if(xbee.getResponse().isError()){
				//ERROR
				Serial.print("ERROR: ");
				Serial.println(xbee.getResponse().getErrorCode());
			}
		}
		delay(1000);
	}
}

boolean sendInitialAlarm(){
	//Flag
	payloadInit[0] = INIT_FLAG; 
	// Time
	currentTime = now();
	payloadInit[1] = currentTime >> 24 & 0xff;
	payloadInit[2] = currentTime >> 16 & 0xff;
	payloadInit[3] = currentTime >> 8 & 0xff;
	payloadInit[4] = currentTime & 0xff;
 	//Enviar mensaje de aviso
 	while(trigger){
 		xbee.send(zbTxInit);
 		if (xbee.readPacket(500)) {
		    // got a response!
		    if (xbee.getResponse().getApiId() == ZB_TX_STATUS_RESPONSE) {
		      	xbee.getResponse().getZBTxStatusResponse(txStatus);
		      	// get the delivery status, the fifth byte
		      	if (txStatus.getDeliveryStatus() == SUCCESS)
		      		trigger = false;
		    }
		}
		delay(1000);
	}

	return true;
}

void sendStatusAlarm(){
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
	//StatusAlarm FLAG
	payloadInit[0] = STATUS_FLAG;
	//StatusAlarm INFO
 	payloadInit[1] = outputChiller0 & 0xff; 
	payloadInit[2] = outputGeneral0 & 0xff;
	payloadInit[3] = outputChiller1 & 0xff;
	payloadInit[4] = outputGeneral1 & 0xff;
	//Send Message
	xbee.send(zbTxStat);
}

void sendStillAlive(){
	//Still Alive FLAG
	payloadAlive[0] = STILL_ALIVE_FLAG;
	xbee.send(zbTxAlive);
}

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


void loop(){
	if(trigger){
		//Send Time 
		trigger_alarm = sendInitialAlarm();
	}
	while(trigger_alarm){
 		sendStatusAlarm();
 		//Check the Alarm status
		trigger_alarm = status();
		//If the alarm set on meanwhile
		if(trigger == true){
			trigger_alarm = true;
		}
		delay(1000);
	}
	//Send StillAliveMSG every 5 min
	if(stillAliveTime + 300 > now()){
		stillAliveTime = now();
		sendStillAlive();
	}
}