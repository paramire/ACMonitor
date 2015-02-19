from xbee import XBee,ZigBee
import serial
import time


PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

# Open serial port
ser = serial.Serial(PORT, BAUD_RATE)

# Create API object
xbee = ZigBee(ser,escaped=True)

DEST_ADDR_LONG = "\x00\x13\xA2\x00\x40\xB1\xD6\x2A"
#DEST_ADDR_LONG = "\x00\x13\xA2\x00\x40\xA7\x92\xDE"
# Continuously read and print packets
count = 0

while True:
    try:
	print "send data"
        xbee.send('tx',dest_addr='\xff\xfe',dest_addr_long=DEST_ADDR_LONG,data=str(count),boradcast_radius='\x00',options='\x01',frame_id='\x01')
	#response = xbee.wait_read_frame()
	#print response
	count+=1	
	time.sleep(2)
    except KeyboardInterrupt:
        break
        
ser.close()
