#!/usr/bin/env python
 
import sys, time
from acmmodules.ACMdaemon import Daemon
 
class MyDaemon(Daemon):
        def run(self):
                while True:
                        time.sleep(20)
                        file = open("newfile.txt", "w")
                        file.write("hello world in the new file\n")
                        file.write("and another line\n")
                        file.close()
 
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
