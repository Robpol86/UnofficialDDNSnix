#!/usr/bin/env python2.6
"""An unofficial dynamic DNS (DDNS) service for Name.com domains.
https://github.com/Robpol86/UnofficialDDNSnix

You must specify (either as command line options or defined in a configuration file) a username,
password, and domain or subdomain name to update with this host's public IP address.

Usage:
    UnofficialDDNS.py -c FILE [-dqv] [-i MINS] [-l FILE] [-n DOMAIN] [-p PASSWD] [-u USER] [--pid FILE]
    UnofficialDDNS.py -n DOMAIN -p PASSWD -u USER [-dqv] [-i MINS] [-l FILE] [--pid FILE]
    UnofficialDDNS.py (-h | --help)
    UnofficialDDNS.py --version

Options:
    -c FILE --config=FILE       Configuration file. Overrides command line options.
    -d --daemon                 Launch as a daemon (runs in the background). Implies --quiet.
    -h --help                   Show this screen.
    -i MINS --interval=MINS     How many minutes to wait before updating (if changed) the domain.
                                [default: 60]
    -l FILE --log=FILE          Log all printed messages to file (rotates monthly).
    -n DOMAIN --domain=DOMAIN   Domain or subdomain name to be updated with the public IP address.
    -p PASSWD --passwd=PASSWD   API password token (NOT your Name.com password).
    --pid=FILE                  Path to optional PID file (enables single-instance enforcement).
    -q --quiet                  Print no messages to terminal.
    -u USER --user=USER         Username of the domain's account holder at the registrar.
    -v --verbose                Include lots of details in messages for troubleshooting.
    --version                   Show version.
"""

from __future__ import division
from __future__ import print_function
from docopt import docopt
from pidfile import PidFile
import atexit
import daemon
import libs
import logging
import logging.config
import os
import signal
import sys
import time


__program__ = 'UnofficialDDNS'
__version__ = '0.0.1'


def decider(session):
    logger = logging.getLogger('%s.decider' % __name__)
    if session.current_ip not in [i.content for i in session.recorded_ips]:
        logger.info("Creating A record.")
        session.create_record()
    for (record, ip) in [(i.id, i.content) for i in session.recorded_ips if i.content == session.current_ip][1:]:
        logger.info("Removing duplicate record ID %s with value %s." % (record, ip))
        session.delete_record(record)
    for (record, ip) in [(i.id, i.content) for i in session.recorded_ips if i.content != session.current_ip]:
        logger.info("Removing old/incorrect record ID %s with value %s." % (record, ip))
        session.delete_record(record)


def main(config):
    logger = logging.getLogger('%s.main' % __name__)
    sleep = config['interval'] * 60

    # Import the registrar's module specified by the user.
    if config['registrar'] == 'name.com':
        from registrar_name import RegistrarName as Registrar

    while True:
        logger.debug("Initializing %s as the context manager." % Registrar.__name__)

        try:
            with Registrar(config) as session:
                logger.info("Current public IP is %s." % session.current_ip)

                if len(session.recorded_ips) != 1:
                    logger.info("Too many records. Updating domain.")
                    decider(session)
                    logger.info("Done making changes.")
                elif session.recorded_ips[0].type != 'A' or session.recorded_ips[0].content != session.current_ip:
                    logger.info("Recorded IP does not match public IP. Updating domain.")
                    decider(session)
                    logger.info("Done making changes.")
                else:
                    logger.info("Recorded IP matches current IP. Nothing to do.")
        except Registrar.RegistrarException as exc:
            message = "An error has occurred while communicating with the registrar."
            if config['verbose']:
                logger.exception(message)
            else:
                logger.error(message)
                logger.error(exc)

        logger.debug("Sleeping for %d seconds" % sleep)
        time.sleep(sleep)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda a, b: sys.exit(0))  # Properly handle Control+C

    # Get CLI args/options and parse config file.
    try:
        main_config = libs.get_config(docopt(__doc__, version=__version__))
    except libs.ConfigError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)

    # Initialize logging.
    umask = 0o027
    os.umask(umask)
    with libs.LoggingSetup(main_config['verbose'], main_config['log'], main_config['quiet']) as cm:
        try:
            logging.config.fileConfig(cm.config)  # Setup logging.
        except IOError:
            print("ERROR: Unable to write to file %s" % main_config['log'], file=sys.stderr)
            sys.exit(1)
    sys.excepthook = lambda t, v, b: logging.critical("Uncaught exception!", exc_info=(t, v, b))  # Log exceptions.
    atexit.register(lambda: logging.info("%s pid %d shutting down." % (__program__, os.getpid())))  # Log when exiting.
    logging.info("Starting %s version %s" % (__program__, __version__))

    # Initialize context manager. Daemonize, use pid file, or both, or none!
    cm = PidFile(main_config['pid']) if main_config['pid'] else None
    if main_config['daemon']:
        cm = daemon.DaemonContext(files_preserve=[h.stream for h in logging.getLogger().handlers],
                                  umask=umask, pidfile=cm)

    # Run the program.
    if cm:
        try:
            with cm:
                if main_config['pid']:
                    logging.debug("Process has daemonized with pid %d successfully." % os.getpid())
                main(main_config)
        except SystemExit as e:
            if "Already running" in str(e):
                logging.error("%s is already running!" % __program__)
                sys.exit(1)
            raise
        except IOError as e:
            if "Permission denied" == e.strerror and e.filename == main_config['pid']:
                logging.error("Failed to write to pid file %s, %s" % (main_config['pid'], e.strerror))
                sys.exit(1)
            raise
    else:
        main(main_config)
