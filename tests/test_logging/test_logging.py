#!/usr/bin/env python2.6
from UnofficialDDNS import __doc__ as uddns_doc
from UnofficialDDNS import __version__ as uddns_ver
from docopt import docopt
import libs
import logging
import logging.config
import logging.handlers
import time


def log_samples():
    """Writes sample log messages to the root logger. Returns the expected timestamp."""
    logging.debug("Test debug testing.")
    logging.info("Test info testing.")
    logging.warn("Test warn testing.")
    logging.error("Test error testing.")
    logging.critical("Test critical testing.")
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def log_samples_named():
    """Same as log_samples() except instead of 'root' it will use its own name in log statements."""
    logger = logging.getLogger('test_logging')
    logger.debug("Test debug testing.")
    logger.info("Test info testing.")
    logger.warn("Test warn testing.")
    logger.error("Test error testing.")
    logger.critical("Test critical testing.")
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def test_default(capsys):
    config = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=['-n', 'x', '-u', 'x', '-p', 'x']))
    with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
        logging.config.fileConfig(f.config)  # Setup logging.
    assert 1 == len(logging.getLogger().handlers)
    assert isinstance(logging.getLogger().handlers[0], libs.LoggingSetup.ConsoleHandler)

    log_samples()
    stdout_actual, stderr_actual = capsys.readouterr()
    stdout_expected = "Test info testing.\n"
    stderr_expected = "Test warn testing.\nTest error testing.\nTest critical testing.\n"
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual


def test_quiet(capsys):
    config = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=['-n', 'x', '-u', 'x', '-p', 'x', '--quiet']))
    with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
        logging.config.fileConfig(f.config)  # Setup logging.
    assert len(logging.getLogger().handlers) == 1
    assert isinstance(logging.getLogger().handlers[0], libs.LoggingSetup.NullHandler)

    log_samples()
    stdout_actual, stderr_actual = capsys.readouterr()
    stdout_expected = ""
    stderr_expected = ""
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual


def test_logfile(capsys, log_file):
    config = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=['-n', 'x', '-u', 'x', '-p', 'x', '--log', log_file.name]))
    with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
        logging.config.fileConfig(f.config)  # Setup logging.
    assert 2 == len(logging.getLogger().handlers)
    assert isinstance(logging.getLogger().handlers[0], libs.LoggingSetup.ConsoleHandler)
    assert isinstance(logging.getLogger().handlers[1], libs.LoggingSetup.TimedRotatingFileHandler)

    timestamp = log_samples()
    stdout_actual, stderr_actual = capsys.readouterr()
    stdout_expected = "Test info testing.\n"
    stderr_expected = "Test warn testing.\nTest error testing.\nTest critical testing.\n"
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    log_actual = log_file.read(1024)
    log_expected = "%s INFO     root                           Test info testing.\n" % timestamp
    log_expected += "%s WARNING  root                           Test warn testing.\n" % timestamp
    log_expected += "%s ERROR    root                           Test error testing.\n" % timestamp
    log_expected += "%s CRITICAL root                           Test critical testing.\n" % timestamp
    assert log_expected == log_actual


def test_verbose(capsys):
    config = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=['-n', 'x', '-u', 'x', '-p', 'x', '--verbose']))
    with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
        logging.config.fileConfig(f.config)  # Setup logging.
    assert len(logging.getLogger().handlers) == 1
    assert isinstance(logging.getLogger().handlers[0], libs.LoggingSetup.ConsoleHandler)

    log_samples()
    stdout_actual, stderr_actual = capsys.readouterr()
    stdout_expected = "Test debug testing.\nTest info testing.\n"
    stderr_expected = "Test warn testing.\nTest error testing.\nTest critical testing.\n"
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual


def test_quiet_logfile(capsys, log_file):
    config = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=['-n', 'x', '-u', 'x', '-p', 'x', '--quiet', '--log', log_file.name]))
    with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
        logging.config.fileConfig(f.config)  # Setup logging.
    assert len(logging.getLogger().handlers) == 1
    assert isinstance(logging.getLogger().handlers[0], libs.LoggingSetup.TimedRotatingFileHandler)

    timestamp = log_samples()
    stdout_actual, stderr_actual = capsys.readouterr()
    stdout_expected = ""
    stderr_expected = ""
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    log_actual = log_file.read(1024)
    log_expected = "%s INFO     root                           Test info testing.\n" % timestamp
    log_expected += "%s WARNING  root                           Test warn testing.\n" % timestamp
    log_expected += "%s ERROR    root                           Test error testing.\n" % timestamp
    log_expected += "%s CRITICAL root                           Test critical testing.\n" % timestamp
    assert log_expected == log_actual


def test_quiet_verbose(capsys):
    config = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=['-n', 'x', '-u', 'x', '-p', 'x', '--quiet', '--verbose']))
    with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
        logging.config.fileConfig(f.config)  # Setup logging.
    assert len(logging.getLogger().handlers) == 1
    assert isinstance(logging.getLogger().handlers[0], libs.LoggingSetup.NullHandler)

    log_samples()
    stdout_actual, stderr_actual = capsys.readouterr()
    stdout_expected = ""
    stderr_expected = ""
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual


def test_logfile_verbose(capsys, log_file):
    config = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=['-n', 'x', '-u', 'x', '-p', 'x', '--verbose', '--log', log_file.name]))
    with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
        logging.config.fileConfig(f.config)  # Setup logging.
    assert 2 == len(logging.getLogger().handlers)
    assert isinstance(logging.getLogger().handlers[0], libs.LoggingSetup.ConsoleHandler)
    assert isinstance(logging.getLogger().handlers[1], libs.LoggingSetup.TimedRotatingFileHandler)

    timestamp = log_samples()
    stdout_actual, stderr_actual = capsys.readouterr()
    stdout_expected = "Test debug testing.\nTest info testing.\n"
    stderr_expected = "Test warn testing.\nTest error testing.\nTest critical testing.\n"
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    log_actual = log_file.read(1024)
    log_expected = "%s DEBUG    root                           Test debug testing.\n" % timestamp
    log_expected += "%s INFO     root                           Test info testing.\n" % timestamp
    log_expected += "%s WARNING  root                           Test warn testing.\n" % timestamp
    log_expected += "%s ERROR    root                           Test error testing.\n" % timestamp
    log_expected += "%s CRITICAL root                           Test critical testing.\n" % timestamp
    assert log_expected == log_actual


def test_quiet_logfile_verbose(capsys, log_file):
    config = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=['-n', 'x', '-u', 'x', '-p', 'x', '--quiet', '--verbose', '--log', log_file.name]))
    with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
        logging.config.fileConfig(f.config)  # Setup logging.
    assert len(logging.getLogger().handlers) == 1
    assert isinstance(logging.getLogger().handlers[0], libs.LoggingSetup.TimedRotatingFileHandler)

    timestamp = log_samples()
    stdout_actual, stderr_actual = capsys.readouterr()
    stdout_expected = ""
    stderr_expected = ""
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    log_actual = log_file.read(1024)
    log_expected = "%s DEBUG    root                           Test debug testing.\n" % timestamp
    log_expected += "%s INFO     root                           Test info testing.\n" % timestamp
    log_expected += "%s WARNING  root                           Test warn testing.\n" % timestamp
    log_expected += "%s ERROR    root                           Test error testing.\n" % timestamp
    log_expected += "%s CRITICAL root                           Test critical testing.\n" % timestamp
    assert log_expected == log_actual


def test_logfile_multiple_loggers(capsys, log_file):
    config = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=['-n', 'x', '-u', 'x', '-p', 'x', '--log', log_file.name]))
    with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
        logging.config.fileConfig(f.config)  # Setup logging.
    assert 2 == len(logging.getLogger().handlers)
    assert isinstance(logging.getLogger().handlers[0], libs.LoggingSetup.ConsoleHandler)
    assert isinstance(logging.getLogger().handlers[1], libs.LoggingSetup.TimedRotatingFileHandler)

    timestamp = log_samples()
    time.sleep(1)
    timestamp_named = log_samples_named()
    stdout_actual, stderr_actual = capsys.readouterr()
    stdout_expected = "Test info testing.\nTest info testing.\n"
    stderr_expected = "Test warn testing.\nTest error testing.\nTest critical testing.\n"
    stderr_expected += "Test warn testing.\nTest error testing.\nTest critical testing.\n"
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    log_actual = log_file.read(1024)
    log_expected = "%s INFO     root                           Test info testing.\n" % timestamp
    log_expected += "%s WARNING  root                           Test warn testing.\n" % timestamp
    log_expected += "%s ERROR    root                           Test error testing.\n" % timestamp
    log_expected += "%s CRITICAL root                           Test critical testing.\n" % timestamp
    log_expected += "%s INFO     test_logging                   Test info testing.\n" % timestamp_named
    log_expected += "%s WARNING  test_logging                   Test warn testing.\n" % timestamp_named
    log_expected += "%s ERROR    test_logging                   Test error testing.\n" % timestamp_named
    log_expected += "%s CRITICAL test_logging                   Test critical testing.\n" % timestamp_named
    assert log_expected == log_actual
