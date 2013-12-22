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
from contextlib import closing
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


def main(config):
    logger = logging.getLogger('%s.main' % __name__)
    sleep = config['interval'] * 60

    # Import the registrar's module specified by the user.
    if config['registrar'] == 'name.com':
        from registrar_name import RegistrarName as Registrar

    while True:
        logger.debug("Initializing %s as the context manager." % Registrar.__name__)

        with Registrar(config) as session:
            try:
                session.get_current_ip()
                logger.info("Current public IP is %s." % session.current_ip)
                session.authenticate()
                session.validate_domain()
                session.get_records()
                if session.current_ip != session.recorded_ip:
                    logger.info("Recorded IP %s does not match public IP. Updating domain." % session.recorded_ip)
                    session.update_record()
                    logger.info("Recorded IP/DNS record is now %s." % session.recorded_ip)
                session.logout()
            except Registrar.RegistrarException:
                logger.exception("An error has occurred while communicating with the registrar.")

        logger.debug("Sleeping for %d seconds" % sleep)
        time.sleep(sleep)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda a, b: sys.exit(0))  # Properly handle Control+C

    # Get CLI args/options and parse config file.
    try:
        config = libs.get_config(docopt(__doc__, version=__version__))
    except libs.ConfigError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)

    # Initialize logging.
    umask = 0o027
    os.umask(umask)
    with closing(libs.generate_logging_config(config)) as f:
        try:
            logging.config.fileConfig(f)  # Setup logging.
        except IOError:
            print("ERROR: Unable to write to file %s" % config['log'], file=sys.stderr)
            sys.exit(1)
    sys.excepthook = lambda t, v, b: logging.critical("Uncaught exception!", exc_info=(t, v, b))  # Log exceptions.
    atexit.register(lambda: logging.info("%s pid %d shutting down." % (__program__, os.getpid())))  # Log when exiting.
    logging.info("Starting %s version %s" % (__program__, __version__))

    # Initialize context manager. Daemonize, use pid file, or both, or none!
    cm = PidFile(config['pid']) if config['pid'] else None
    if config['daemon']:
        cm = daemon.DaemonContext(files_preserve=[h.stream for h in logging.getLogger().handlers],
                                  umask=umask, pidfile=cm)

    # Run the program.
    if cm:
        try:
            with cm:
                if config['pid']:
                    logging.debug("Process has daemonized with pid %d successfully." % os.getpid())
                main(config)
        except SystemExit as e:
            if "Already running" in str(e):
                logging.error("%s is already running!" % __program__)
                sys.exit(1)
            raise
        except IOError as e:
            if "Permission denied" == e.strerror and e.filename == config['pid']:
                logging.error("Failed to write to pid file %s, %s" % (config['pid'], e.strerror))
                sys.exit(1)
            raise
    else:
        main(config)
