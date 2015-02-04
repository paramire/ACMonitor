import sys
import time
from daemon import Daemon
from xbee import XBee

class BeeWatchDog:
	def run(self):
		xbee = XBee(ser)
		ser = serial.Serial('/dev/tty01', 9600)
		while True:
			# Continuously read and print packets
			while True:
			    try:
			        response = xbee.wait_read_frame()
			        print response
			    except KeyboardInterrupt:
			        break
			        
			ser.close()
			time.sleep(1)

class MyDaemon(Daemon):
	def run(self):
		bwd = BeeWatchDog()
		bwd.run()

if __name__ == "__main__":
	daemon = MyDaemon('/tmp/bwd-daemon.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknow"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage %s start|stop|restart" % sys.argv[0]
		sys.exit(2)