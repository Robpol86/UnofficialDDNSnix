#!/usr/bin/env python2.6
"""An unofficial dynamic DNS (DDNS) service for Name.com domains.
https://github.com/Robpol86/UnofficialDDNSnix

Usage:
    UnofficialDDNS.py -c FILE [-dqv] [-i MINS] [-l FILE] [-n DOMAIN] [-p PASSWD] [-u USER]
    UnofficialDDNS.py -n DOMAIN -p PASSWD -u USER [-dqv] [-i MINS] [-l FILE]
    UnofficialDDNS.py (-h | --help)
    UnofficialDDNS.py --version

Options:
    -c FILE --config=FILE           Configuration file. Overrides command line options.
    -d --daemon                     Launch as a daemon (runs in the background).
    -h --help                       Show this screen.
    -i MINS --interval=MINS         How many minutes to wait before updating (if changed) the domain.
                                    [default: 60]
    -l FILE --log=FILE              Log all printed messages to file (rotates monthly).
    -n DOMAIN --domain=DOMAIN       Domain or subdomain name to be updated with the public IP address.
    -p PASSWD --passwd=PASSWD       API password token (NOT your Name.com password).
    -q --quiet                      Print no messages to terminal.
    -u USER --user=USER             Username of the domain's account holder at the registrar.
    -v --verbose                    Include lots of details in messages for troubleshooting.
    --version                       Show version.
"""

from __future__ import division
from __future__ import print_function
from contextlib import closing
from libs import print
from docopt import docopt
import libs
import logging
import logging.config
import signal
import sys


__version__ = '1.0.0'


def main(config):
    pass


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda a, b: sys.exit(0))  # Properly handle Control+C
    try:
        config = libs.get_config(docopt(__doc__, version=__version__))  # Get CLI args/options and parse config file.
    except libs.ConfigError as e:
        config = dict()
        print("ERROR: %s" % e.message, file=sys.stderr, term=1)
    with closing(libs.generate_logging_config(config)) as f:
        try:
            logging.config.fileConfig(f)
        except IOError:
            print("ERROR: Unable to write to file %s" % config['log'], file=sys.stderr, term=1)
    main(config)

