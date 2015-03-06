import sys, os, time
from threading import Thread
from datetime import datetime
from acmmodules.ACMdaemon import Daemon
import acmmodules.ACMXbee as ACMXbee
import acmmodules.ACMmqtt as ACMmqtt
import acmmodules.ACMsqlite as ACMsqlite
import acmmodules.ACMconfig as ACMconfig

def arduino_status(acm_mqtt, acm_config):
    """Check the status of the arduino and send the apropiate MQTT msg

    Initialize a SQLite connection, for future query
    every 2,5 min, check if the last Keep_alive entry in the database its
    in the 5 min gap (which the arduino send the packet)
    - If its in the 5 min gap - send a MQTT status CONNECTED message
    - If its not in the 5 min gap check if on a ALARM mode (alarm date
    newer than finish date)
        - alarm mode ON: Alarm date > Finish date: CONNECTED ALARM ON
        - alarm mode OFF: Alarm date < Finish date: DISCONNECTED
    - IF the keep_alive table empty - DISCONNECTED 

    Args:
        acm_mqtt(mqtt connection): MQTT connection Object
        acm_mqtt(Object): Config Object

    Returns:
        None
    """
    acm_sqlite_conf = acm_config.getConf('sqlite')
    acm_sqlite = ACMsqlite.acmDB(acm_sqlite_conf['db_dir'],acm_sqlite_conf['xbee_csv'])

    while True:
        time.sleep(150)
        now = int(time.time())
        keep_alive = acm_sqlite.select(0x21,where='id = (SELECT MAX(id) FROM ' + acm_sqlite.table_name[0x21] + ')',fetch_one=True)
        if len(keep_alive) > 0:
            if now - keep_alive[3] > 300:
                alarm = acm_sqlite.select(0x55,where='id = (SELECT MAX(id) FROM ' + acm_sqlite.table_name[0x55] + ')',fetch_one=True)
                finish = acm_sqlite.select(0xAA,where='id = (SELECT MAX(id) FROM ' + acm_sqlite.table_name[0xAA] + ')',fetch_one=True)
                if len(alarm) & len(finish):
                    if alarm[0] > finish[0]:
                        acm_mqtt.sendStatus(time=now,connected=True,alert=0)
                    else:
                        acm_mqtt.sendStatus(time=now,connected=False)
                else:
                    acm_mqtt.sendStatus(time=now,connected=False)
            else:
                acm_mqtt.sendStatus(time=now,connected=True,alert=1)
        else:
            acm_mqtt.sendStatus(time=now,connected=True,alert=2)

def arduino_watch(acm_mqtt, acm_config):
    """Watch the XBEE messages

    Init the SQLite Connection
    Init the XBee Connection

    Wait until a Message arrive to the BBB XBee (managed by ACMXbee Module),
    Return the data managed to the check the type of packet

    Prepare the date of the moment, and the source address of the Xbee

    - Time Request: 
        Insert in the SQLite Database a row in Time Table, send the Requested Time
        Send a MQTT message of Time_request/Init
    - Keep Alive
        Insert in the SQLite Database a row in keep_alive Table,
        Send a MQTT message of the Keep_alive
    - Alarm
        Insert in the SQLite Database a row in the Alarm Table,
        Send a General Alarm MQTT Message
    - Alarm On 
        Check which specific alarm are On
        Insert in the SQLite Database a row in the Alarm_On Table with the information
        of which alarm its on
        Send a MQTT message with the specific alarm its activated
    - Finish
        Insert in the SQLite Database a row in Finish Table
        send a MQTT message of the Finish of the Alarm
    - Error 
        Insert in the SQLite Database a row in Error Table
        send a MQTT message of the Error of the Alarm
    - Other
        Insert in the SQLite Database a row in Other Table

    Args:
        acm_mqtt(ACMmqtt connection): ACMmqtt object which manage the connection
        acm_config(ACMconfig object): ACMconfig object which manage the configurations

    Returns:
        None

    """
    acm_sqlite_conf = acm_config.getConf('sqlite')
    acm_sqlite = ACMsqlite.acmDB(acm_sqlite_conf['db_dir'],acm_sqlite_conf['xbee_csv'])
    
    acm_xbee_conf = acm_config.getConf('xbee','uart')
    acm_xbee = ACMXbee.acmXbee('\x00\x13\xA2\x00\x40\xB1\xD6\x2A',port=acm_xbee_conf['port'],baud=acm_xbee_conf['baud'])

    while True:
        try:
            packet, data = acm_xbee.wait_res()
            if data['id'] == 'rx':
                
                #print hex(data['source_addr_long'])
                code = ":".join("{:02x}".format(ord(c)) for c in data['source_addr_long'])
                bbb_date_u = int(time.time())
                bbb_date_t = datetime.fromtimestamp(bbb_date_u).strftime("%d-%m-%Y %H:%M:%S")

                #Time request
                if packet['flag'] == 0x0F:
                    acm_sqlite.insert(0x0F,code=code,date_t=bbb_date_t,date_u=bbb_date_u)
                    acm_xbee.send_time(bbb_date_u)
                    acm_mqtt.sendInit(time=bbb_date_t)

                #Keep Alive
                elif packet['flag'] == 0x21:
                    acm_sqlite.insert(0x21,code=code,date_t=bbb_date_t,date_u=bbb_date_u)
                    acm_mqtt.sendKeep(time=bbb_date_t)
                #Alarm
                elif packet['flag'] == 0x55:
                    acm_sqlite.insert(0x55,code=code,date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])
                    acm_mqtt.sendAlarm(time=bbb_date_t)
                    #SNMP-TRAP

                #Alarm on
                elif packet['flag'] == 0x56:
                    if packet['tres'] < packet['alm1']:                                     
                        acm_sqlite.insert(0x56,code=code,name='alm1',scan=packet['alm1'],date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])
                        acm_mqtt.sendAlarmOn(time=bbb_date_t,topic='chiller1',value=packet['alm1'])
                    
                    if packet['tres'] < packet['alm2']:                                     
                        acm_sqlite.insert(0x56,code=code,name='alm2',scan=packet['alm2'],date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])
                        acm_mqtt.sendAlarmOn(time=bbb_date_t,topic='general1',value=packet['alm2'])
                    
                    if packet['tres'] < packet['alm3']:
                        acm_sqlite.insert(0x56,code=code,name='alm3',scan=packet['alm3'],date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])                                   
                        acm_mqtt.sendAlarmOn(time=bbb_date_t,topic='chiller2',value=packet['alm3'])
                    
                    if packet['tres'] < packet['alm4']:                                     
                        acm_sqlite.insert(0x56,code=code,name='alm4',scan=packet['alm4'],date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])
                        acm_mqtt.sendAlarmOn(time=bbb_date_t,topic='general2',value=packet['alm4'])

                #Finish
                elif packet['flag'] == 0xAA:
                    acm_sqlite.insert(0xAA,code=code,date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])
                    acm_mqtt.sendFinish(time=bbb_date_t)

                #Error
                elif packet['flag'] == 0xFF:
                    acm_sqlite.insert(0xFF,code=code,date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'],errc=packet['errc'])
                    acm_mqtt.sendErrorXbee(time=bbb_date_t,error=packet['errc'])
                
                elif packet['flag'] == 0x01:
                    acm_sqlite.insert(0x01,code=code,date_t=bbb_date_t,date_u=bbb_date_u,err=packet['err'])

            elif data['id'] == 'tx_status':
                #print "Response: " + str(packet['status'])
                pass
        except KeyboardInterrupt:
            break


class MyDaemon(Daemon):
    def run(self):
        """Main function
        
        Prepare the ACMmqtt object and Configurations
        
        Create the Threads for Arduino_status and Arduino_Watch
        
        Args:
            None
        
        Returns:
            None
        """
        os.chdir("/home/pramirez/proyects/ACM/ACM/")
        acm_config = ACMconfig.acmConfigParser()
        acm_mqtt_conf = acm_config.getConf('mqtt')
        acm_mqtt = ACMmqtt.acmMQTT(acm_mqtt_conf['dest_ip'],acm_mqtt_conf['dest_port'],acm_mqtt_conf['topic_will'],acm_mqtt_conf['last_will'],True)
        thread_watch = Thread(target = arduino_watch, args=(acm_mqtt,acm_config,))
        thread_alarm = Thread(target = arduino_status, args=(acm_mqtt,acm_config,))
        thread_alarm.start()
        thread_watch.start()
        thread_alarm.join()
        acm_mqtt.close()
 
if __name__ == "__main__":
    #main()
    daemon = MyDaemon('/tmp/acm.pid',stdout="/var/log/acm.log",stderr="/var/log/acm.err")
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)