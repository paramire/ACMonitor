from xbee import Xbee, ZigBee
import Adafruit_BBIO.UART as UART
from serial, time


class acmXbee(object):

	def __init__(self,port='/dev/ttyO1',baud=9600,uart='UART1',end_point):
		self.port = port
		self.baud = baud
		self.dest_addr_long = end_point
		self.dest_addr = '\xff\xfe'
		UART.setup(UART1)

		#Init Serial
		self.ser = serial.Serial(port,baud)
		#Init ZigBee-Xbee
		self.xbee = ZigBee(self.ser,Escaped=True)

	def _get_data(response):
		tag = response['rf_data']
		var = {}
		var['source'] = self._get_code(response['source_addr_long'])
		var['flag'] = tag[0:2]

		if tag[0:2] == 0x01: 
			var.update(self._recieve_time_request())
		elif tag[0:2] == 0x02:
			var.update(self._recieve_alarm_request())
		elif tag[0:2] == 0x03:
			var.update(_recieve_alarm_on_request())
		elif tag[0:2] == 0x04:
			var.update(self._recieve_keep_alive_request)
		else:
			var.update(self._recieve_other())
		return var

	def wait_res(self):
		response = self.xbee.wait_read_frame()
		return self._get_data(response)

	def _recieve_time_request():
		pass

	def _recieve_alarm_request():
		pass

	def _recieve_alarm_on_request():
		pass

	def _recieve_keep_alive_request():
		pass

	def _recieve_other():
		pass

	def send_time(code,ts_unix):
		xbee.send('tx',data=str(ts_unix),dest_addr=self.dest_addr,dest_addr_long=code,broadcast_radius='\x00',options='\x01')
		#WAIT TX status?
		return 0

	def ser_close():
		self.ser.close()
		pass