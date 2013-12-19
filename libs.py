#!/usr/bin/env python2.6
"""Classes and functions for UnofficialDDNSnix.
https://github.com/Robpol86/UnofficialDDNSnix
"""

from __future__ import division
from __future__ import print_function
import StringIO
import logging
import logging.handlers
import os
import re
import sys


class ConfigError(Exception):
    """Raised when insufficient/invalid config file or CLI options are given."""
    pass


class ConsoleHandler(logging.StreamHandler):
    """A handler that logs to console in the sensible way.

    StreamHandler can log to *one of* sys.stdout or sys.stderr.

    It is more sensible to log to sys.stdout by default with only error
    (logging.WARNING and above) messages going to sys.stderr. This is how
    ConsoleHandler behaves.

    http://code.activestate.com/recipes/576819-logging-to-console-without-surprises/

    Modified by Robpol86.
    """

    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        self.stream = sys.stderr if record.levelno >= logging.WARNING else sys.stdout
        logging.StreamHandler.emit(self, record)

    def flush(self):
        # Workaround a bug in logging module
        # See:
        #   http://bugs.python.org/issue6333
        if self.stream and hasattr(self.stream, 'flush') and not self.stream.closed:
            logging.StreamHandler.flush(self)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


def generate_logging_config(config):
    """Generates a StringIO pseudo file handler to be passed to logging.config.fileConfig. Use it with "with"."""
    draft = StringIO.StringIO()
    final = StringIO.StringIO()
    level = "INFO" if not config['verbose'] else "DEBUG"
    log = config['log']
    quiet = any([config['quiet'], config['daemon']])

    # Write static data to the pseudo config file.
    draft.write(
        """
        [formatters]
        keys=console,file

        [formatter_console]
        format=%(message)s

        [formatter_file]
        format=%(asctime)s %(levelname)-8s %(name)-15s %(message)s
        datefmt=%Y-%m-%dT%H:%M:%S

        [loggers]
        keys=root

        [handler_null]
        class=libs.NullHandler
        args=()
        """
    )

    # Add handlers.
    handlers = []
    if not quiet:
        handlers.append('console')
        draft.write(
            """
            [handler_console]
            class=libs.ConsoleHandler
            level=DEBUG
            formatter=console
            args=()
            """
        )
    if log:
        handlers.append('file')
        draft.write(
            """
            [handler_file]
            class=logging.handlers.TimedRotatingFileHandler
            level=DEBUG
            formatter=file
            args=('%s','D',30,5)
            """ % log
        )
    if not handlers:
        handlers.append('null')
    draft.write(
        """
        [logger_root]
        level=%s
        handlers=%s

        [handlers]
        keys=%s
        """ % (level, ','.join(handlers), ','.join(handlers))
    )

    # Finish up.
    draft.seek(0)
    final.writelines(("%s\n" % line for line in (l.strip() for l in draft) if line))
    draft.close()
    final.seek(0)
    return final


def get_config(cli_args, test=False):
    """Reads command line arguments/options and (if provided) reads/overrides settings from config file."""
    config = dict(daemon=False, quiet=False, verbose=False, interval=60, log=None, domain=None, passwd=None, user=None)
    # Read from command line.
    for option, value in ((o[2:], v) for o, v in cli_args.iteritems() if o[2:] in config):
        if option in ('daemon', 'quiet', 'verbose') and value:
            # User set one of these options to true (by specifying the flag).
            config[option] = True
        elif option == 'interval':
            if not value.isdigit():
                raise ConfigError("%s in command line must be an integer only." % option)
            value = int(value)
            if not value:
                raise ConfigError("%s in command line must be greater than 0." % option)
            config[option] = value
        elif option == 'log' and value:
            if not os.path.exists(os.path.dirname(value)):
                raise ConfigError("Parent directory of log file does not exist.")
            config[option] = value
        elif value:
            config[option] = value

    # Read from configuration file, if specified. Overrides command line.
    config_file = dict()
    if '--config' in cli_args and cli_args['--config']:
        if not os.path.isfile(cli_args['--config']):
            raise ConfigError("Specified config file %s does not exist or is not a file." % cli_args['--config'])
        try:
            with open(cli_args['--config'], 'r') as f:
                for line in (l.strip() for l in f):
                    split = re.split(r"\s*", line.lower(), maxsplit=2)
                    if len(split) != 2 or split[0] not in config:
                        raise ConfigError("Invalid line in config file: %s" % line)
                    config_file[split[0]] = split[1]
        except IOError:
            raise ConfigError("Unable to read file %s" % cli_args['--config'])
    for option, value in config_file.iteritems():
        if option in ('daemon', 'quiet', 'verbose'):
            if value == 'true':
                config[option] = True
            elif value == 'false':
                config[option] = False
            else:
                raise ConfigError("%s in config file must be true or false only." % option)
        elif option == 'interval':
            if not value.isdigit():
                raise ConfigError("%s in config file must be an integer only." % option)
            value = int(value)
            if not value:
                raise ConfigError("%s in config file must be greater than 0." % option)
            config[option] = value
        elif option == 'log':
            if not os.path.exists(os.path.dirname(value)):
                raise ConfigError("Parent directory of log file does not exist.")
            config[option] = value
        else:
            config[option] = value

    # Now make sure we got everything we need.
    if (not config['domain'] or not config['user'] or not config['passwd']) and not test:
        raise ConfigError("A domain, username, and password must be specified.")

    # Done.
    return config