from xbee import XBee, ZigBee
#import Adafruit_BBIO.UART as UART
import serial, time
from datetime import datetime

class acmXbee(object):

	def __init__(self,end_point,port='/dev/ttyO1',baud=9600,uart=None):
		"""__init__ acmXbee

		Init the Xbee, the serial connection, the mode (Xbee serie 1 or 2)

		Args:
			endpoint (string): String of the Destination XBee
			port (string): serial Port
			baud (int): baud
			uart (string):  If it's in the Beaglebone it's needed to activate
				the correct UART
		Returns:
			None
		"""
		self.port = port
		self.baud = baud
		self.dest_addr_long = end_point
		self.dest_addr = '\xff\xfe'

		#Init UART
		if uart != None:
			UART.setup(uart)
		
		#Open Serial
		self.ser = serial.Serial(port,baud,timeout=5)
		if not(self.ser.isOpen()):
			self.ser.open()

		#Init ZigBee-Xbee
		self.xbee = ZigBee(self.ser,escaped=True)

	def _hex_timestamp(self,timestamp):
		"""Internal Function, transform a HEX timestamp to 
		correct value.
	
		Returns:
			ts (integer): Timestamp
		"""
		ts = 0
		if(len(timestamp) == 4):
			for i in range(0,4):
				ts = (ts | ord(timestamp[i]))
				if i != 3:
					ts = ts << 8
		return ts

	def _timestamp_hex(self,ts_unix):
		"""Internal Function, transform a timestamp in a
		payload of 8 bit each(HEX) (string array)
	
		Returns:
			ts (string): timestamp to String (HEX)

		"""
		ts = ''
		ts_aux = ts_unix
		for i in range(3,-1,-1):
			ts_aux = (ts_unix >> 8*i) & 0xFF
			ts += str(chr(ts_aux))
		return ts

	def wait_res(self):
		"""Wait packet from the XBee

		Wait from a packet from the XBEE, syncronichous function
		will not release the thread until a message is procesed

		Args:
			None
		Returns:
			Data of the response
		"""
		response = self.xbee.wait_read_frame()
		return self._get_data(response)

	def _get_data(self,response):
		"""Internal Function which send the Packet to the correct
		function

		Internal Function which send the Packet to the correct
		function, and recieve the procesed data to later be sended

		Args:
			response (string): data xbee response
		Returns:
			Procesed data (var), and all the response  
		"""
		var = {}
		if response['id'] == 'rx':
			acm_packet = response['rf_data']
			#Time Request
			if ord(acm_packet[0]) == 0x0F:
				var.update(self._receive_time_request(acm_packet))
			#Keep Alive
			elif ord(acm_packet[0]) == 0x21:
				var.update(self._receive_keep_alive_request(acm_packet))
			#Alarm
			elif ord(acm_packet[0]) == 0x55:
				var.update(self._receive_alarm_request(acm_packet))
			#Alarm on
			elif ord(acm_packet[0]) == 0x56:
				var.update(self._receive_alarm_on_request(acm_packet))
			#FINISH
			elif ord(acm_packet[0]) == 0xAA:
				var.update(self._receive_finish_request(acm_packet))
			#ERROR
			elif ord(acm_packet[0]) == 0xFF:
				var.update(self._receive_error_request(acm_packet))
			#OTHER
			else:
				var['flag'] = 0x01
				var['err'] = response['rf_data']
		elif response['id'] == 'tx_status':
			var['status'] = response['deliver_status']
		return [var,response]

	def _receive_time_request(self,packet):
		"""
		Internal Function which manage the Time Request Packet 

		Internal Function which manage the Time Request Packet recieved from 
		the Arduino, process the packet data to a dictionary
		
		Args:
			packet (string): data
		Returns:
			Data Time Request Packet 
		"""
		return {'flag':ord(packet[0])}

	def _receive_keep_alive_request(self,packet):
		"""
		Internal Function which manage the Keep Alive Packet 

		Internal Function which manage the Keep Alive Packet recieved from 
		the Arduino, process the packet data to a dictionary
		
		Args:
			packet (string): data
		Returns:
			Data Keep Alive Packet 
		"""
		return {'flag':ord(packet[0])}

	def _receive_alarm_request(self,packet):
		"""
		Internal Function which manage the Alarm Packet 

		Internal Function which manage the Alarm Packet recieved from 
		the Arduino, process the packet data to a dictionary
		
		Args:
			packet (string): data
		Returns:
			Data Alarm Packet 
		"""
		res = {}
		if len(packet) == 5:
			res['flag'] = ord(packet[0])
			res['ts_u'] = self._hex_timestamp(packet[1:5])
			res['ts_d'] = datetime.fromtimestamp(res['ts_u']).strftime("%d-%m-%Y %H:%M:%S")
		return res

	def _receive_alarm_on_request(self,packet):
		"""
		Internal Function which manage the Alarm on Packet 

		Internal Function which manage the Alarm on Packet recieved from 
		the Arduino, process the packet data to a dictionary
		
		Args:
			packet (string): data
		Returns:
			Data Alarm on Packet 
		"""
		res = {}
		if len(packet) == 10:
			res['flag'] = ord(packet[0])
			res['ts_u'] = self._hex_timestamp(packet[1:5])
			res['ts_d'] = datetime.fromtimestamp(res['ts_u']).strftime("%d-%m-%Y %H:%M:%S")
			res['tres'] = ord(packet[5])
			res['alm1'] = ord(packet[6])
			res['alm2'] = ord(packet[7])
			res['alm3'] = ord(packet[8])
			res['alm4'] = ord(packet[9])
		return res

	def _receive_finish_request(self,packet):
		"""
		Internal Function which manage the Finish Packet 

		Internal Function which manage the Finish Packet recieved from 
		the Arduino, process the packet data to a dictionary
		
		Args:
			packet (string): data
		Returns:
			Data Finish Packet 
		"""
		res = {}
		if len(packet) == 5:
			res['flag'] = ord(packet[0])
			res['ts_u'] = self._hex_timestamp(packet[1:5])
			res['ts_d'] = datetime.fromtimestamp(res['ts_u']).strftime("%d-%m-%Y %H:%M:%S")
		return res

	def _receive_error_request(self,packet):
		"""
		Internal Function which manage the Error Packet 

		Internal Function which manage the Error Packet recieved from 
		the Arduino, process the packet data to a dictionary
		
		Args:
			packet (string): data
		Returns:
			Data Error Packet 
		"""
		res = {}
		if len(packet) == 6:
			res['flag'] = ord(packet[0])
			res['ts_u'] = self._hex_timestamp(packet[1:5])
			res['ts_d'] = datetime.fromtimestamp(res['ts_u']).strftime("%d-%m-%Y %H:%M:%S")
			res['errc'] = ord(packet[5])
		return res

	def send_time(self,ts_unix):
		"""Send the TIME RESPONSE to XBee

		Send the TIME RESPONSE to XBEE, with the saved data send it to the 
		target XBee

		Args:
			ts_unix(int): Timestamp 
		Returns:
			None	
		"""
		self.xbee.send('tx',data=self._timestamp_hex(ts_unix),dest_addr=self.dest_addr,dest_addr_long=self.dest_addr_long,broadcast_radius='\x00',options='\x01')

	def ser_close(self):
		"""Close the Serial connection
		Returns:
			None
		"""
		self.ser.close()