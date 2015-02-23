from threading import Thread
from datetime import datetime
from ACMdaemon import Daemon
import ACMsqlite, ACMXbee, ACMmqtt
import sys, os, time
 
def main_alarm(acm_mqtt):
        while True:
            try:
                time.sleep(30)
                bbb_date_u = int(time.time())
                acm_mqtt.sendTopic('keep',time=bbb_date_u)              
            except KeyboardInterrupt:
                break

def main_watch(acm_mqtt):

        while True:
            try:
                bbb_date_u = int(time.time())
                acm_mqtt.sendTopic('init',time=bbb_date_u)
                time.sleep(60)                        
            except KeyboardInterrupt:
                break
            finally:
                acm_mqtt.close()


class MyDaemon(Daemon):
    def run(self):
        while True:
            acm_mqtt = ACMmqtt.acmMQTT('127.0.0.1',1883,"ACM/BBB/status","ERROR: BBB Lost",looped=True)
            thread_watch = Thread(target = main_watch, args=(acm_mqtt,))
            thread_alarm = Thread(target = main_alarm, args=(acm_mqtt,))
            thread_alarm.start()
            thread_watch.start()
            thread_alarm.join()
 
if __name__ == "__main__":
    daemon = MyDaemon('/tmp/daemon-example.pid')
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