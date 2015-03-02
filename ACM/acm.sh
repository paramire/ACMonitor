### BEGIN INIT INFO
# Provides:          mylistener
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     S
# Default-Stop:      0 6
# Short-Description: This is the description.
# Description:       This is the description.
### END INIT INFO

DAEMON=/usr/bin/python
ARGS=/home/pramirez/proyects/ACM/ACM/ACM.py
PIDFILE=/tmp/acm-daemon.pid

case "$1" in
  start)
    echo "starting service"
    /sbin/start-stop-daemon --start --pidfile $PIDFILE \
        --user www-data --group www-data \
        -b --make-pidfile \
        --chuid www-data \
        --exec $DAEMON $ARGS
    ;;
  stop)
    echo "stopping service"
    /sbin/start-stop-daemon --stop --pidfile $PIDFILE --verbose
    ;;
  *)
    echo "Useage: /etc/init.d/mylistener {start|stop}"
    exit 1
    ;;
esac

exit 0