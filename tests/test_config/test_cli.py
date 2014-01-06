#!/usr/bin/env python2.6
import pytest
from UnofficialDDNS import __doc__ as uddns_doc
from UnofficialDDNS import __version__ as uddns_ver
from docopt import docopt
import libs


def test_config_file_and_cli_complimentary_with_full_valid_data(config_file):
    config_file.write("domain: mydomain.com")
    config_file.flush()
    argv = ['-c', config_file.name, '-u', 'usera', '-p', 'pass']
    expected = dict(log=None, daemon=False, verbose=False, interval=60, pid=None, quiet=False, version=False,
                    registrar='name.com', config=config_file.name, help=False,
                    user='usera', passwd='pass', domain='mydomain.com')
    actual = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert expected == actual


def test_config_file_and_cli_overlapping_with_full_valid_data(config_file):
    config_file.write("domain: mydomain2.com")
    config_file.flush()
    argv = ['-c', config_file.name, '-n', 'abc.com', '-u', 'usera', '-p', 'pass']
    expected = dict(log=None, daemon=False, verbose=False, interval=60, pid=None, quiet=False, version=False,
                    registrar='name.com', config=config_file.name, help=False,
                    user='usera', passwd='pass', domain='mydomain2.com')
    actual = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert expected == actual


def test_config_file_and_cli_overlapping_with_incomplete_data(config_file):
    config_file.write("domain: mydomain3.com")
    config_file.flush()
    argv = ['-c', config_file.name, '-n', 'abc.com', '-u', 'usera']
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "A domain, username, and password must be specified." == str(e.value)


def test_cli_invalid_options():
    argv = ['-n', 'test.com', '-p', 'testpw', '-u', 'testuser', '-d', 'shouldBeFlag']
    with pytest.raises(SystemExit):
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))


def test_cli_interval_fail():
    argv = ['-n', 'test.com', '-p', 'testpw', '-u', 'testuser', '-i', 'shouldBeNum']
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Config option 'interval' must be a number." == str(e.value)
    argv = ['-n', 'test.com', '-p', 'testpw', '-u', 'testuser', '-i', '0']
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Config option 'interval' must be greater than 0." == str(e.value)


def test_cli_pass():
    argv = ['-n', 'test.com', '-p', 'testpw', '-u', 'testuser']
    expected = dict(log=None, daemon=False, verbose=False, interval=60, pid=None, quiet=False, version=False,
                    registrar='name.com', config=None, help=False,
                    user='testuser', passwd='testpw', domain='test.com')
    actual = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert expected == actual
