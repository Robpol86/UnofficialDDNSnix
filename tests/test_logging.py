#!/usr/bin/env python2.6
import libs
import logging
import logging.config
import logging.handlers
import sys
import tempfile
import time
import unittest


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
    logger = logging.getLogger(__name__)
    logger.debug("Test debug testing.")
    logger.info("Test info testing.")
    logger.warn("Test warn testing.")
    logger.error("Test error testing.")
    logger.critical("Test critical testing.")
    return time.strftime("%Y-%m-%dT%H:%M:%S")


class TestLogging(unittest.TestCase):
    def setUp(self):
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        if not hasattr(sys.stderr, "getvalue"):
            self.fail("need to run in buffered mode for stderr too!")
        self.log_file = tempfile.NamedTemporaryFile()
        self.maxDiff = None

    def tearDown(self):
        self.log_file.close()

    def test_default(self):
        config = libs.get_config(dict(), test=True)
        with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
            logging.config.fileConfig(f.config)  # Setup logging.
        self.assertEqual(len(logging.getLogger().handlers), 1)
        self.assertIsInstance(logging.getLogger().handlers[0], libs.LoggingSetup.ConsoleHandler)

        log_samples()
        stdout_actual = sys.stdout.getvalue()
        stderr_actual = sys.stderr.getvalue()
        stdout_expected = "Test info testing.\n"
        stderr_expected = "Test warn testing.\nTest error testing.\nTest critical testing.\n"
        self.assertEqual(stdout_actual, stdout_expected)
        self.assertEqual(stderr_actual, stderr_expected)

    def test_quiet(self):
        config = libs.get_config({'--quiet': True}, test=True)
        with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
            logging.config.fileConfig(f.config)  # Setup logging.
        self.assertEqual(len(logging.getLogger().handlers), 1)
        self.assertIsInstance(logging.getLogger().handlers[0], libs.LoggingSetup.NullHandler)

        log_samples()
        stdout_actual = sys.stdout.getvalue()
        stderr_actual = sys.stderr.getvalue()
        stdout_expected = ""
        stderr_expected = ""
        self.assertEqual(stdout_actual, stdout_expected)
        self.assertEqual(stderr_actual, stderr_expected)

    def test_logfile(self):
        config = libs.get_config({'--log': self.log_file.name}, test=True)
        with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
            logging.config.fileConfig(f.config)  # Setup logging.
        self.assertEqual(len(logging.getLogger().handlers), 2)
        self.assertIsInstance(logging.getLogger().handlers[0], libs.LoggingSetup.ConsoleHandler)
        self.assertIsInstance(logging.getLogger().handlers[1], libs.LoggingSetup.TimedRotatingFileHandler)

        timestamp = log_samples()
        stdout_actual = sys.stdout.getvalue()
        stderr_actual = sys.stderr.getvalue()
        stdout_expected = "Test info testing.\n"
        stderr_expected = "Test warn testing.\nTest error testing.\nTest critical testing.\n"
        self.assertEqual(stdout_actual, stdout_expected)
        self.assertEqual(stderr_actual, stderr_expected)

        log_actual = self.log_file.read(1024)
        log_expected = "%s INFO     root                           Test info testing.\n" % timestamp
        log_expected += "%s WARNING  root                           Test warn testing.\n" % timestamp
        log_expected += "%s ERROR    root                           Test error testing.\n" % timestamp
        log_expected += "%s CRITICAL root                           Test critical testing.\n" % timestamp
        self.assertMultiLineEqual(log_actual, log_expected)

    def test_verbose(self):
        config = libs.get_config({'--verbose': True}, test=True)
        with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
            logging.config.fileConfig(f.config)  # Setup logging.
        self.assertEqual(len(logging.getLogger().handlers), 1)
        self.assertIsInstance(logging.getLogger().handlers[0], libs.LoggingSetup.ConsoleHandler)

        log_samples()
        stdout_actual = sys.stdout.getvalue()
        stderr_actual = sys.stderr.getvalue()
        stdout_expected = "Test debug testing.\nTest info testing.\n"
        stderr_expected = "Test warn testing.\nTest error testing.\nTest critical testing.\n"
        self.assertEqual(stdout_actual, stdout_expected)
        self.assertEqual(stderr_actual, stderr_expected)

    def test_quiet_logfile(self):
        config = libs.get_config({'--quiet': True, '--log': self.log_file.name}, test=True)
        with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
            logging.config.fileConfig(f.config)  # Setup logging.
        self.assertEqual(len(logging.getLogger().handlers), 1)
        self.assertIsInstance(logging.getLogger().handlers[0], libs.LoggingSetup.TimedRotatingFileHandler)

        timestamp = log_samples()
        stdout_actual = sys.stdout.getvalue()
        stderr_actual = sys.stderr.getvalue()
        stdout_expected = ""
        stderr_expected = ""
        self.assertEqual(stdout_actual, stdout_expected)
        self.assertEqual(stderr_actual, stderr_expected)

        log_actual = self.log_file.read(1024)
        log_expected = "%s INFO     root                           Test info testing.\n" % timestamp
        log_expected += "%s WARNING  root                           Test warn testing.\n" % timestamp
        log_expected += "%s ERROR    root                           Test error testing.\n" % timestamp
        log_expected += "%s CRITICAL root                           Test critical testing.\n" % timestamp
        self.assertMultiLineEqual(log_actual, log_expected)

    def test_quiet_verbose(self):
        config = libs.get_config({'--quiet': True, '--verbose': True}, test=True)
        with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
            logging.config.fileConfig(f.config)  # Setup logging.
        self.assertEqual(len(logging.getLogger().handlers), 1)
        self.assertIsInstance(logging.getLogger().handlers[0], libs.LoggingSetup.NullHandler)

        log_samples()
        stdout_actual = sys.stdout.getvalue()
        stderr_actual = sys.stderr.getvalue()
        stdout_expected = ""
        stderr_expected = ""
        self.assertEqual(stdout_actual, stdout_expected)
        self.assertEqual(stderr_actual, stderr_expected)

    def test_logfile_verbose(self):
        config = libs.get_config({'--log': self.log_file.name, '--verbose': True}, test=True)
        with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
            logging.config.fileConfig(f.config)  # Setup logging.
        self.assertEqual(len(logging.getLogger().handlers), 2)
        self.assertIsInstance(logging.getLogger().handlers[0], libs.LoggingSetup.ConsoleHandler)
        self.assertIsInstance(logging.getLogger().handlers[1], libs.LoggingSetup.TimedRotatingFileHandler)

        timestamp = log_samples()
        stdout_actual = sys.stdout.getvalue()
        stderr_actual = sys.stderr.getvalue()
        stdout_expected = "Test debug testing.\nTest info testing.\n"
        stderr_expected = "Test warn testing.\nTest error testing.\nTest critical testing.\n"
        self.assertEqual(stdout_actual, stdout_expected)
        self.assertEqual(stderr_actual, stderr_expected)

        log_actual = self.log_file.read(1024)
        log_expected = "%s DEBUG    root                           Test debug testing.\n" % timestamp
        log_expected += "%s INFO     root                           Test info testing.\n" % timestamp
        log_expected += "%s WARNING  root                           Test warn testing.\n" % timestamp
        log_expected += "%s ERROR    root                           Test error testing.\n" % timestamp
        log_expected += "%s CRITICAL root                           Test critical testing.\n" % timestamp
        self.assertMultiLineEqual(log_actual, log_expected)

    def test_quiet_logfile_verbose(self):
        config = libs.get_config({'--quiet': True, '--log': self.log_file.name, '--verbose': True}, test=True)
        with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
            logging.config.fileConfig(f.config)  # Setup logging.
        self.assertEqual(len(logging.getLogger().handlers), 1)
        self.assertIsInstance(logging.getLogger().handlers[0], libs.LoggingSetup.TimedRotatingFileHandler)

        timestamp = log_samples()
        stdout_actual = sys.stdout.getvalue()
        stderr_actual = sys.stderr.getvalue()
        stdout_expected = ""
        stderr_expected = ""
        self.assertEqual(stdout_actual, stdout_expected)
        self.assertEqual(stderr_actual, stderr_expected)

        log_actual = self.log_file.read(1024)
        log_expected = "%s DEBUG    root                           Test debug testing.\n" % timestamp
        log_expected += "%s INFO     root                           Test info testing.\n" % timestamp
        log_expected += "%s WARNING  root                           Test warn testing.\n" % timestamp
        log_expected += "%s ERROR    root                           Test error testing.\n" % timestamp
        log_expected += "%s CRITICAL root                           Test critical testing.\n" % timestamp
        self.assertMultiLineEqual(log_actual, log_expected)

    def test_logfile_multiple_loggers(self):
        config = libs.get_config({'--log': self.log_file.name}, test=True)
        with libs.LoggingSetup(config['verbose'], config['log'], config['quiet']) as f:
            logging.config.fileConfig(f.config)  # Setup logging.
        self.assertEqual(len(logging.getLogger().handlers), 2)
        self.assertIsInstance(logging.getLogger().handlers[0], libs.LoggingSetup.ConsoleHandler)
        self.assertIsInstance(logging.getLogger().handlers[1], libs.LoggingSetup.TimedRotatingFileHandler)

        timestamp = log_samples()
        time.sleep(1)
        timestamp_named = log_samples_named()
        stdout_actual = sys.stdout.getvalue()
        stderr_actual = sys.stderr.getvalue()
        stdout_expected = "Test info testing.\nTest info testing.\n"
        stderr_expected = "Test warn testing.\nTest error testing.\nTest critical testing.\n"
        stderr_expected += "Test warn testing.\nTest error testing.\nTest critical testing.\n"
        self.assertEqual(stdout_actual, stdout_expected)
        self.assertEqual(stderr_actual, stderr_expected)

        log_actual = self.log_file.read(1024)
        log_expected = "%s INFO     root                           Test info testing.\n" % timestamp
        log_expected += "%s WARNING  root                           Test warn testing.\n" % timestamp
        log_expected += "%s ERROR    root                           Test error testing.\n" % timestamp
        log_expected += "%s CRITICAL root                           Test critical testing.\n" % timestamp
        log_expected += "%s INFO     test_logging                   Test info testing.\n" % timestamp_named
        log_expected += "%s WARNING  test_logging                   Test warn testing.\n" % timestamp_named
        log_expected += "%s ERROR    test_logging                   Test error testing.\n" % timestamp_named
        log_expected += "%s CRITICAL test_logging                   Test critical testing.\n" % timestamp_named
        self.assertMultiLineEqual(log_actual, log_expected)


if __name__ == "__main__":
    unittest.main(buffer=True)
