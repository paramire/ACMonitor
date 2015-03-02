#!/bin/sh -e
### BEGIN INIT INFO
# Provides:          dachs
# Required-Start:    $local_fs $remote_fs $network
# Required-Stop:     $local_fs $remote_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start/stop ACM system
# Description:       Startup script to control (start, stop and reload)
#                    the python ACM system
### END INIT INFO
#
DAEMON="/usr/bin/python"
ARGS="ACM.py"

case $1 in
	start)
		echo $DAEMON $ARGS
	;;
	stop)
		log_daemon_msg "Stopping VO server" "dachs"
	;;
	reload | force-reload)
		log_daemon_msg "Reloading VO server config" "dachs"
	;;
	restart)
		log_daemon_msg "Restarting VO server" "dachs"
	;;
	*)
		log_success_msg "Usage: /etc/init.d/dachs {start|stop|restart|reload|force-reload}"
		exit 1
	;;
esac
