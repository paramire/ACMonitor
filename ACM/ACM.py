from threading import Thread
from datetime import datetime
from ACMdaemon import Daemon
import ACMsqlite, ACMXbee
import sys, os, time
 
def main_alarm():
        acm_sqlite = ACMsqlite.acmDB('database/acm.bd','files/xbee_data.csv')
        if acm_sqlite.check():
            print "SQLite" + str(acm_sqlite.nameDB) + " is Open"

        while True:
            try:
                time.sleep(30)
                now = int(time.time())
                keep_alive = acm_sqlite.select(0x21,'id = (SELECT MAX(id) FROM ' + acm_sqlite.table_name[0x21] + ')')
                #print keep_alive[0][3]
                if now - keep_alive[0][3] > 300:
                    print 'run'
                    #SNMP-TRAP
                else:
                    print 'dont run'               
            except KeyboardInterrupt:
                break

def main_watch():

        acm_sqlite = ACMsqlite.acmDB('database/acm.bd','files/xbee_data.csv')
        if acm_sqlite.check():
            print "SQLite" + str(acm_sqlite.nameDB) + " is Open"

        acm_xbee = ACMXbee.acmXbee('\x00\x13\xA2\x00\x40\xB1\xD6\x2A',port='/dev/ttyUSB0',baud=9600)

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
                    #Keep Alive
                    elif packet['flag'] == 0x21:
                        acm_sqlite.insert(0x21,code=code,date_t=bbb_date_t,date_u=bbb_date_u)
                    #Alarm
                    elif packet['flag'] == 0x55:
                        acm_sqlite.insert(0x55,code=code,date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])
                        #SNMP-TRAP
                    #Alarm on
                    elif packet['flag'] == 0x56:
                        if packet['tres'] < packet['alm1']:                                     
                            acm_sqlite.insert(0x56,code=code,name='alm1',scan=packet['alm1'],date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])
                        if packet['tres'] < packet['alm2']:                                     
                            acm_sqlite.insert(0x56,code=code,name='alm2',scan=packet['alm2'],date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])
                        if packet['tres'] < packet['alm3']:
                            acm_sqlite.insert(0x56,code=code,name='alm3',scan=packet['alm3'],date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])                                   
                        if packet['tres'] < packet['alm4']:                                     
                            acm_sqlite.insert(0x56,code=code,name='alm4',scan=packet['alm4'],date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])
                        #SNMP-TRAP
                    #Finish
                    elif packet['flag'] == 0xAA:
                        acm_sqlite.insert(0xAA,code=code,date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'])
                    #Error
                    elif packet['flag'] == 0xFF:
                        acm_sqlite.insert(0xFF,code=code,date_t=bbb_date_t,date_u=bbb_date_u,a_date_t=packet['ts_d'],a_date_u=packet['ts_u'],errc=packet['errc'])
                    elif packet['flag'] == 0x01:
                        acm_sqlite.insert(0x01,code=code,date_t=bbb_date_t,date_u=bbb_date_u,err=packet['err'])
                elif data['id'] == 'tx_status':
                    print "Response: " + str(packet['status'])
                    pass
            except KeyboardInterrupt:
                break


class MyDaemon(Daemon):
    def run(self):
        while True:
            thread_watch = Thread(target = main_watch)
            thread_alarm = Thread(target = main_alarm)
            thread_alarm.start()
            thread_watch.start()
 
if __name__ == "__main__":

    thread_watch = Thread(target = main_watch)
    thread_alarm = Thread(target = main_alarm)
    thread_alarm.start()
    thread_watch.start()
    #daemon = MyDaemon('/tmp/daemon-example.pid')
    #if len(sys.argv) == 2:
    #    if 'start' == sys.argv[1]:
    #        daemon.start()
    #    elif 'stop' == sys.argv[1]:
    #        daemon.stop()
    #    elif 'restart' == sys.argv[1]:
    #        daemon.restart()
    #    else:
    #        print "Unknown command"
    #        sys.exit(2)
    #    sys.exit(0)
    #else:
    #    print "usage: %s start|stop|restart" % sys.argv[0]
    #    sys.exit(2)
