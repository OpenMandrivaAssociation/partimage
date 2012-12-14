#!/bin/sh
#
# description: Runs partimage server
# chkconfig: 345 90 60
#
### BEGIN INIT INFO
# Provides:          partimaged
# Required-Start:    $remote_fs $network
# Required-Stop:     $remote_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Partition Image Server
# Description:       Partition Image Server let's you backup partitions from
#                    a client to a server.
#                    All data is transferred encrypted using SSL.
### END INIT INFO
# Source function library.
. /etc/rc.d/init.d/functions

. /etc/sysconfig/partimaged

[ -n "$JAIL" -a ! -d "$JAIL" ] && exit 0

RETVAL=0

#
#	See how we were called.
#

prog="partimaged"

# don't avoid killing processes not running in the same root
inmyroot() {
	echo "$*"
}

start() {
	# Check if partimaged is already running
	if [ ! -f /var/lock/subsys/partimaged ]; then
	    ARGS=
	    if [ -n "$JAIL" ]; then
		ARGS="--chroot $JAIL -n -L"
	    fi
	    gprintf "Starting %s: " "$prog"
	    daemon /usr/sbin/partimaged -D $ARGS
	    RETVAL=$?
	    [ $RETVAL -eq 0 ] && touch /var/lock/subsys/partimaged
	    echo
	fi
	return $RETVAL
}

stop() {
	gprintf "Stopping %s: " "$prog"
	killproc /usr/sbin/partimaged
	RETVAL=$?
	[ $RETVAL -eq 0 ] && rm -f /var/lock/subsys/partimaged
	echo
        return $RETVAL
}


restart() {
	stop
	start
}	

reload() {
	restart
}	

status_at() {
 	status /usr/sbin/partimaged
}

case "$1" in
start)
	start
	;;
stop)
	stop
	;;
reload|restart)
	restart
	;;
condrestart)
	if [ -f /var/lock/subsys/partimaged ]; then
	    restart
	fi
	;;
status)
	status_at
	;;
*)
	gprintf "Usage: %s {start|stop|restart|condrestart|status}\n" "$0"
	exit 1
esac

exit $?
exit $RETVAL
