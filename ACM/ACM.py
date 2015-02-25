import sys, os, time
from threading import Thread
from datetime import datetime
from acmmodules.ACMdaemon import Daemon
import acmmodules.ACMXbee as ACMXbee
import acmmodules.ACMmqtt as ACMmqtt
import acmmodules.ACMsqlite as ACMsqlite
import daemon

def arduino_status(acm_mqtt):

        acm_sqlite = ACMsqlite.acmDB('database/acm.bd','files/xbee_data.csv')
        #if acm_sqlite.check():p
        #    print "SQLite" + str(acm_sqlite.nameDB) + " is Open"

        while True:
            time.sleep(10)
            now = int(time.time())
            keep_alive = acm_sqlite.select(0x21,where='id = (SELECT MAX(id) FROM ' + acm_sqlite.table_name[0x21] + ')',fetch_one=True)
            if now - keep_alive[3] > 300:
                alarm = acm_sqlite.select(0x55,where='id = (SELECT MAX(id) FROM ' + acm_sqlite.table_name[0x55] + ')',fetch_one=True)
                finish = acm_sqlite.select(0xAA,where='id = (SELECT MAX(id) FROM ' + acm_sqlite.table_name[0xAA] + ')',fetch_one=True)
                if len(alarm) & len(finish):
                    if alarm[0] > finish[0]:
                        acm_mqtt.sendStatus(time=now,connected=True,alert=True)
                    else:
                        acm_mqtt.sendStatus(time=now,connected=False)
                else:
                    acm_mqtt.sendStatus(time=now,connected=False)
            else:
                acm_mqtt.sendStatus(time=now,connected=True,alert=False)

def arduino_watch(acm_mqtt):

        acm_xbee = ACMXbee.acmXbee('\x00\x13\xA2\x00\x40\xB1\xD6\x2A',port='/dev/ttyUSB0',baud=9600)
        acm_sqlite = ACMsqlite.acmDB('database/acm.bd','files/xbee_data.csv')
        #if acm_sqlite.check():
        #    print "SQLite" + str(acm_sqlite.nameDB) + " is Open"

        while True:
            try:
                packet, data = acm_xbee.wait_res()
                #manage_packet(packet,data)
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


def main():
    acm_mqtt = ACMmqtt.acmMQTT('localhost',1883,"ACM/BBB/status","ERROR: BBB Lost",True)
    thread_watch = Thread(target = arduino_watch, args=(acm_mqtt,))
    thread_alarm = Thread(target = arduino_status, args=(acm_mqtt,))
    thread_alarm.start()
    thread_watch.start()
    thread_alarm.join()
    acm_mqtt.close()
 
if __name__ == "__main__":
    main()