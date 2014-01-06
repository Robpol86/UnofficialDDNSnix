#!/usr/bin/env python2.6
"""Classes and functions for UnofficialDDNSnix.
https://github.com/Robpol86/UnofficialDDNSnix
"""

from __future__ import division
from __future__ import print_function
import StringIO
import functools
import logging
import logging.handlers
import os
import re
import sys
import yaml
import yaml.parser
import yaml.reader
import yaml.scanner


# noinspection PyCallingNonCallable
class Color(str):
    """Converts {color} tags to Bash color codes. However len() will show the length of visible colors and not include \
    the invisible color codes."""

    _codes = dict(b=1, i=3, u=4, flash=5, outline=6, negative=7, invis=8, strike=9, black=30, red=31, green=32,
                  brown=33, blue=34, purple=35, cyan=36, gray=37, bgblack=40, bgred=41, bggreen=42, bgbrown=43,
                  bgblue=44, bgpurple=45, bgcyan=46, bggray=47, hiblack=90, hired=91, higreen=92, hibrown=93, hiblue=94,
                  hipurple=95, hicyan=96, higray=97, hibgblack=100, hibgred=101, hibggreen=102, hibgbrown=103,
                  hibgblue=104, hibgpurple=105, hibgcyan=106, hibggray=107, pink=95, yellow=93, white=97, bgyellow=103,
                  bgpink=105, bgwhite=107)
    _codes.update({'/all': 0, '/attr': 10, '/b': 22, '/i': 23, '/u': 24, '/flash': 25, '/outline': 26, '/negative': 27,
                   '/strike': 29, '/fg': 39, '/bg': 49})
    _codes_parsed = dict([(k, "\033[%sm" % v) for k, v in _codes.iteritems()])

    def __new__(cls, value):
        parsed = str(value.format(**cls._codes_parsed))
        for p in [(sub, sub.replace("m\033[", ';')) for sub in re.compile(r"((?:\033\[[\d;]+m){2,})").findall(parsed)]:
            parsed = str.replace(parsed, p[0], p[1])  # Merge consecutive formatting.
        obj = str.__new__(cls, parsed)
        obj.stripped = str(re.compile(r"\033\[[\d;]+m").sub('', parsed))
        return obj

    def __len__(self):
        return str.__len__(self.stripped)

    def _case(self):
        """Fix bash color code casing."""
        @functools.wraps(self)
        def wrapped(inst, *args, **kwargs):
            return re.sub(r"\033\[([\d;]+)M", r"\033\[\1m", self(inst, *args, **kwargs))
        return wrapped

    def _stp(self):
        """String to parsed conversion."""
        @functools.wraps(self)
        def wrapped(inst, *args, **kwargs):
            return str.replace(self(inst, *args, **kwargs), inst.stripped, inst)
        return wrapped

    def _color(self):
        """Converts string type outputs to Color type."""
        @functools.wraps(self)
        def wrapped(inst, *args, **kwargs):
            return Color(self(inst, *args, **kwargs))
        return wrapped

    for f in ['center', 'ljust', 'rjust', 'zfill']:
        exec("@_stp\n@_color\ndef {0}(self, *args, **kwargs): return str.{0}(self.stripped, *args, **kwargs)".format(f))

    for f in ['join', 'lower', 'lstrip', 'replace', 'rstrip', 'strip']:
        exec("@_color\ndef {0}(self, *args, **kwargs): return str.{0}(self, *args, **kwargs)".format(f))

    for f in ['swapcase', 'upper']:
        exec("@_case\n@_color\ndef {0}(self, *args, **kwargs): return str.{0}(self, *args, **kwargs)".format(f))

    for f in ['rsplit', 'split']:
        exec("def {0}(self, *args, **kwargs): return [Color(s) for s in str.{0}(self, *args, **kwargs)]".format(f))

    def title(self, *args, **kwargs):
        """Don't use: Can't figure out how to implement this properly."""
        raise NotImplementedError


class LoggingSetup(object):
    """Generates a StringIO pseudo file handler to be passed to logging.config.fileConfig. Use it with "with"."""

    def __init__(self, verbose=False, log_file='', console_quiet=False):
        self.level = "INFO" if not verbose else "DEBUG"
        self.log_file = log_file
        self.console_quiet = console_quiet
        self.draft = StringIO.StringIO()
        self.config = StringIO.StringIO()

    def __enter__(self):
        self.generate_draft()
        self.draft_to_config()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.draft.close()
        self.config.close()

    class ConsoleHandler(logging.StreamHandler):
        """A handler that logs to console in the sensible way.

        StreamHandler can log to *one of* sys.stdout or sys.stderr.

        It is more sensible to log to sys.stdout by default with only error
        (logging.WARNING and above) messages going to sys.stderr. This is how
        ConsoleHandler behaves.

        http://code.activestate.com/recipes/576819-logging-to-console-without-surprises/

        Modified by @Robpol86.
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

    class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler, object):
        """Overrides TimedRotatingFileHandler to support the Color class. Gets rid of colors from file logging."""
        def emit(self, record):
            if isinstance(record, Color):
                record = record.stripped
            super(LoggingSetup.TimedRotatingFileHandler, self).emit(record)

    def generate_draft(self):
        """Create a first draft of the pseudo config file for logging."""
        # Write static data to the pseudo config file.
        self.draft.write(
            """
            [formatters]
            keys=console,file

            [formatter_console]
            format=%(message)s

            [formatter_file]
            format=%(asctime)s %(levelname)-8s %(name)-30s %(message)s
            datefmt=%Y-%m-%dT%H:%M:%S

            [loggers]
            keys=root

            [handler_null]
            class=libs.LoggingSetup.NullHandler
            args=()
            """
        )

        # Add handlers.
        handlers = []
        if not self.console_quiet:
            handlers.append('console')
            self.draft.write(
                """
                [handler_console]
                class=libs.LoggingSetup.ConsoleHandler
                level=DEBUG
                formatter=console
                args=()
                """
            )
        if self.log_file:
            handlers.append('file')
            self.draft.write(
                """
                [handler_file]
                class=libs.LoggingSetup.TimedRotatingFileHandler
                level=DEBUG
                formatter=file
                args=('%s','D',30,5)
                """ % self.log_file
            )
        if not handlers:
            handlers.append('null')
        self.draft.write(
            """
            [logger_root]
            level={level}
            handlers={handlers}

            [handlers]
            keys={handlers}
            """.format(level=self.level, handlers=','.join(handlers))
        )

    def draft_to_config(self):
        self.draft.seek(0)
        self.config.writelines(("%s\n" % line for line in (l.strip() for l in self.draft) if line))
        self.config.seek(0)


class MultipleConfigSources(object):
    """Handles configuration options from command line and YAML config file."""
    def __init__(self, docopt_parsed, config_file):
        self.docopt_parsed = dict([(o[2:], v) for o, v in docopt_parsed.iteritems()])
        if not config_file:
            self.config_file_parsed = dict()
            return
        if not os.path.isfile(config_file):
            raise self.ConfigError("Config file %s does not exist, not a file, or no permission." % config_file)
        try:
            with open(config_file, 'rb') as f:
                self.config_file_parsed = yaml.load(f)
        except IOError:
            raise self.ConfigError("Unable to read config file %s." % config_file)
        except yaml.reader.ReaderError:
            raise self.ConfigError("Unable to read config file %s, invalid data." % config_file)
        except (yaml.scanner.ScannerError, yaml.parser.ParserError) as e:
            if r"found character '\t' that cannot start any token" in str(e):
                raise self.ConfigError("Tab character found in config file %s. Must use spaces only!" % config_file)
            raise self.ConfigError("Config file %s contents not YAML formatted: %s" % (config_file, e))
        if not isinstance(self.config_file_parsed, dict):
            raise self.ConfigError(
                "Config file %s contents didn't yield dict or not YAML: %s" % (config_file, self.config_file_parsed)
            )
        for key in self.config_file_parsed:
            if key not in self.docopt_parsed:
                raise self.ConfigError("Unknown option %s in config file %s." % (key, config_file))
            if isinstance(self.docopt_parsed[key], bool) and not isinstance(self.config_file_parsed[key], bool):
                raise self.ConfigError("Config file option %s must be True or False." % key)

    class ConfigError(Exception):
        """Raised when insufficient/invalid config file or CLI options are given."""
        pass

    def merge(self):
        """Merges command line options and config file options, config file taking precedence."""
        config = self.docopt_parsed.copy()
        for key, value in config.iteritems():
            if isinstance(value, str) and value.isdigit():
                config[key] = int(value)
        for key, value in self.config_file_parsed.iteritems():
            config[key] = value
        return config


def get_config(cli_args, test=False):
    """Verifies all the required config options for UnofficialDDNS are satisfied."""
    # Read from multiple sources and get final config.
    multi_config = MultipleConfigSources(cli_args, cli_args.get('--config', ''))
    config = multi_config.merge()
    if test:
        # Skip checks if testing.
        return config
    config['registrar'] = 'name.com'  # In the future I might support other registrars.

    # Validate interval.
    if not isinstance(config['interval'], int):
        raise multi_config.ConfigError("Config option 'interval' must be a number.")
    if not config['interval']:
        raise multi_config.ConfigError("Config option 'interval' must be greater than 0.")

    # Validate pid and log.
    for option in ('log', 'pid'):
        if not config[option]:
            continue
        parent = os.path.dirname(config[option])
        if not os.path.exists(parent):
            raise multi_config.ConfigError("Parent directory %s of %s file does not exist." % (parent, option))
        if not os.access(parent, os.W_OK):
            raise multi_config.ConfigError("Parent directory %s of %s file not writable." % (parent, option))

    # Now make sure we got everything we need.
    if not all([config.get(o, None) for o in ('domain', 'user', 'passwd')]):
        raise multi_config.ConfigError("A domain, username, and password must be specified.")

    # Done.
    return config