#!/usr/bin/env python2.6
"""An unofficial dynamic DNS (DDNS) service for Name.com domains.
https://github.com/Robpol86/UnofficialDDNSnix

You must specify (either as command line options or defined in a configuration file) a username,
password, and domain or subdomain name to update with this host's public IP address.

Usage:
    UnofficialDDNS.py -c FILE [-dqv] [-i MINS] [-l FILE] [-n DOMAIN] [-p PASSWD] [-u USER]
    UnofficialDDNS.py -n DOMAIN -p PASSWD -u USER [-dqv] [-i MINS] [-l FILE]
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
    -q --quiet                  Print no messages to terminal.
    -u USER --user=USER         Username of the domain's account holder at the registrar.
    -v --verbose                Include lots of details in messages for troubleshooting.
    --version                   Show version.
"""

from __future__ import division
from __future__ import print_function
from contextlib import closing
from docopt import docopt
import atexit
import daemon
import libs
import logging
import logging.config
import os
import signal
import sys


__program__ = 'UnofficialDDNS'
__version__ = '0.0.1'


def main(config):
    pass


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda a, b: sys.exit(0))  # Properly handle Control+C

    # Get CLI args/options and parse config file.
    try:
        config = libs.get_config(docopt(__doc__, version=__version__))
    except libs.ConfigError as e:
        print("ERROR: %s" % e.message, file=sys.stderr)
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

    # Daemonize if desired. Otherwise run program normally.
    if config['daemon']:
        with daemon.DaemonContext(files_preserve=[h.stream for h in logging.getLogger().handlers], umask=umask):
            logging.debug("Process has daemonized with pid %d successfully." % os.getpid())
            main(config)
    else:
        main(config)
