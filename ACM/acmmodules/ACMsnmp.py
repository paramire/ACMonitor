from pysnmp.entity.rfc3413.oneliner import ntforg

class acmSNMP(object):

	def __init__(self,cd,port,):
		self.ntforg = ntforg.NotificationOriginator()
		self.communityData = cd
		self.port = port

	def sendAlarm(self):
		errorIndication = self.ntforg.sendNotification(
            ntforg.CommunityData(self.communityData),
            ntforg.UdpTransportTarget(('localhost',162)),
            'trap',
            ntforg.MibVariable('SNMPv2-MIB','coldStart'),
            (ntforg.MibVariable('SNMPv2-MIB','sysName',0),'new name'))

	def sendKeepAlive(self):
		self.ntforg.sendNotification(
	        ntforg.CommunityData(self.communityData),
	        ntforg.UdpTransportTarget(('localhost',162)),
	        'trap',
	        ntforg.MibVariable('SNMPv2-MIB','coldStart'),
	        (ntforg.MibVariable('SNMPv2-MIB','sysName'),'new name'))