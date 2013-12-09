#!/usr/bin/env python2.6
import os
import tempfile
from docopt import docopt
from UnofficialDDNS import __doc__ as uddns_doc
from UnofficialDDNS import __version__ as uddns_ver
import libs
import unittest


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.expected = libs.get_config(dict(), test=True)
        self.config_file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        self.config_file.close()

    def test_config_file_only_with_invalid_binary_data(self):
        self.config_file.write(os.urandom(1024))
        self.config_file.flush()
        argv = ['-c', self.config_file.name]
        with self.assertRaises(libs.ConfigError) as cm:
            libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.assertIn("Invalid line in config file", cm.exception.message)

    def test_config_file_only_with_nonexistent_file(self):
        argv = ['-c', '/tmp/doesNotExist.28520']
        with self.assertRaises(libs.ConfigError) as cm:
            libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.assertIn("does not exist", cm.exception.message)

    def test_config_file_only_with_no_read_permissions(self):
        argv = ['-c', '/etc/sudoers']
        with self.assertRaises(libs.ConfigError) as cm:
            libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.assertIn("Unable to read file", cm.exception.message)

    def test_config_file_only_with_directory_instead_of_file(self):
        argv = ['-c', '/etc']
        with self.assertRaises(libs.ConfigError) as cm:
            libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.assertIn("does not exist", cm.exception.message)

    def test_config_file_only_with_invalid_text_data(self):
        self.config_file.write("Test\n")
        self.config_file.flush()
        argv = ['-c', self.config_file.name]
        with self.assertRaises(libs.ConfigError) as cm:
            libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.assertIn("Invalid line in config file", cm.exception.message)

    def test_config_file_only_with_full_valid_data(self):
        self.config_file.write("domain mydomain.com\nuser thisuser\npasswd abc")
        self.config_file.flush()
        argv = ['-c', self.config_file.name]
        actual = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.expected['domain'] = 'mydomain.com'
        self.expected['passwd'] = 'abc'
        self.expected['user'] = 'thisuser'
        self.assertEqual(actual, self.expected)

    def test_config_file_and_cli_complimentary_with_full_valid_data(self):
        self.config_file.write("domain mydomain.com")
        self.config_file.flush()
        argv = ['-c', self.config_file.name, '-u', 'usera', '-p', 'pass']
        actual = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.expected['domain'] = 'mydomain.com'
        self.expected['passwd'] = 'pass'
        self.expected['user'] = 'usera'
        self.assertEqual(actual, self.expected)

    def test_config_file_and_cli_overlapping_with_full_valid_data(self):
        self.config_file.write("domain mydomain2.com")
        self.config_file.flush()
        argv = ['-c', self.config_file.name, '-n', 'abc.com', '-u', 'usera', '-p', 'pass']
        actual = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.expected['domain'] = 'mydomain2.com'
        self.expected['passwd'] = 'pass'
        self.expected['user'] = 'usera'
        self.assertEqual(actual, self.expected)

    def test_config_file_and_cli_overlapping_with_incomplete_data(self):
        self.config_file.write("domain mydomain3.com")
        self.config_file.flush()
        argv = ['-c', self.config_file.name, '-n', 'abc.com', '-u', 'usera']
        self.expected['domain'] = 'mydomain2.com'
        self.expected['passwd'] = 'pass'
        self.expected['user'] = 'usera'
        with self.assertRaises(libs.ConfigError) as cm:
            libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.assertEqual("A domain, username, and password must be specified.", cm.exception.message)

    def test_cli_invalid_options(self):
        argv = ['-n', 'test.com', '-p', 'testpw', '-u', 'testuser', '-d', 'shouldBeFlag']
        with self.assertRaises(SystemExit):
            libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))

    def test_cli_interval_fail(self):
        argv = ['-n', 'test.com', '-p', 'testpw', '-u', 'testuser', '-i', 'shouldBeNum']
        with self.assertRaises(libs.ConfigError) as cm:
            libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.assertIn("integer only", cm.exception.message)
        argv = ['-n', 'test.com', '-p', 'testpw', '-u', 'testuser', '-i', '0']
        with self.assertRaises(libs.ConfigError) as cm:
            libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.assertIn("greater than 0", cm.exception.message)

    def test_cli_pass(self):
        argv = ['-n', 'test.com', '-p', 'testpw', '-u', 'testuser']
        actual = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
        self.expected['domain'] = 'test.com'
        self.expected['passwd'] = 'testpw'
        self.expected['user'] = 'testuser'
        self.assertEqual(actual, self.expected)


if __name__ == "__main__":
    unittest.main()

