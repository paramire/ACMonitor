import csv,random,time
from datetime import datetime

"""
CREATE SOME TEST CSV FILES
-ALARM
-FINISH
-TIME
"""

def main():
	code = '00:13:a2:00:40:b1:d6:2a'
	with open('xbee_time.csv','w') as f:
		a = csv.writer(f,delimiter=',')
		data=[]
		for i in range(0,10):
		 	now = int(time.time()) + random.randrange(86400*i,86400+86400*i)
		 	date = datetime.fromtimestamp(now).strftime("%d-%m-%Y %H:%M:%S")
		 	data.append([code,now,date])
		a.writerows(data)

	data_b=[]
	with open('xbee_alarm.csv','w') as f:
		b = csv.writer(f,delimiter=',')
		data=[]
		for i in range(0,10):
		 	now = int(time.time()) + random.randrange(86400*i,86400+86400*i)
		 	date = datetime.fromtimestamp(now).strftime("%d-%m-%Y %H:%M:%S")
		 	date_a = datetime.fromtimestamp(now-10).strftime("%d-%m-%Y %H:%M:%S")
		 	date_b = datetime.fromtimestamp(now+3600)
		 	data.append([code,now,date,now-10,date_a])
		 	data_b.append([code,now+300,date_b,now+300,date_b])
		b.writerows(data)

	with open('xbee_finish.csv','w') as f:
		c = csv.writer(f,delimiter=',')
		c.writerows(data_b)
if __name__ == '__main__':
	main()