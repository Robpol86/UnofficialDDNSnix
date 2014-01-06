#!/bin/bash
#
# UnofficialDDNS Unofficial dynamic DNS (DDNS) service.
#
# chkconfig:     2345 20 80
# description:   {{SUMMARY}}
#                {{URL}}
# config:        /etc/UnofficialDDNS.yaml
# pidfile:       /var/UnofficialDDNS/UnofficialDDNS.pid
 
### BEGIN INIT INFO
# Provides: UnofficialDDNS
# Required-Start: $named
# Required-Stop:
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Unofficial dynamic DNS (DDNS) service.
# Description: {{SUMMARY}}
#              {{URL}}
### END INIT INFO

. /etc/rc.d/init.d/functions

exec="/usr/share/UnofficialDDNS/UnofficialDDNS.py"
prog="UnofficialDDNS"
config="/etc/UnofficialDDNS.yaml"

lockfile=/var/lock/subsys/$prog

start() {
    [ -x $exec ] || exit 5
    [ -f $config ] || exit 6
    echo -n $"Starting $prog: "
    daemon --user uddns $exec -qc /etc/$prog.yaml
    retval=$?
    echo
    [ $retval -eq 0 ] && touch $lockfile
    return $retval
}

stop() {
    echo -n $"Stopping $prog: "
    killproc -p /var/UnofficialDDNS/UnofficialDDNS.pid $prog
    retval=$?
    echo
    [ $retval -eq 0 ] && rm -f $lockfile
    return $retval
}

restart() {
    stop
    start
}

rh_status() {
    # run checks to determine if the service is running or use generic status
    status -p /var/UnofficialDDNS/UnofficialDDNS.pid $prog
}

rh_status_q() {
    rh_status >/dev/null 2>&1
}

case "$1" in
    start)
        rh_status_q && exit 0
        $1
        ;;
    stop)
        rh_status_q || exit 0
        $1
        ;;
    restart)
        $1
        ;;
    reload)
        rh_status_q || exit 7
        restart
        ;;
    force-reload)
        restart
        ;;
    status)
        rh_status
        ;;
    condrestart|try-restart)
        rh_status_q || exit 0
        restart
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart|condrestart|reload}"
        exit 2
esac
exit $?
