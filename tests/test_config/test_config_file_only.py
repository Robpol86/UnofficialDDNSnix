#!/usr/bin/env python2.6
import os
import pytest
from UnofficialDDNS import __doc__ as uddns_doc
from UnofficialDDNS import __version__ as uddns_ver
from docopt import docopt
import libs


def test_config_file_only_with_invalid_binary_data(config_file):
    config_file.write(os.urandom(1024))
    config_file.flush()
    argv = ['-c', config_file.name]
    with pytest.raises(libs.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Invalid line in config file." == str(e.value)


def test_config_file_only_with_nonexistent_file():
    argv = ['-c', '/tmp/doesNotExist.28520']
    with pytest.raises(libs.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Specified config file /tmp/doesNotExist.28520 does not exist or is not a file." == str(e.value)


def test_config_file_only_with_no_read_permissions():
    argv = ['-c', '/etc/sudoers']
    with pytest.raises(libs.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Unable to read file /etc/sudoers" == str(e.value)


def test_config_file_only_with_directory_instead_of_file():
    argv = ['-c', '/etc']
    with pytest.raises(libs.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Specified config file /etc does not exist or is not a file." == str(e.value)


def test_config_file_only_with_invalid_text_data(config_file):
    config_file.write("Test\n")
    config_file.flush()
    argv = ['-c', config_file.name]
    with pytest.raises(libs.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Invalid line in config file: Test" == str(e.value)


def test_config_file_only_with_full_valid_data(config_file):
    config_file.write("domain mydomain.com\nuser thisuser\npasswd abc")
    config_file.flush()
    argv = ['-c', config_file.name]
    expected = libs.get_config(dict(), test=True)
    expected['domain'] = 'mydomain.com'
    expected['passwd'] = 'abc'
    expected['user'] = 'thisuser'
    actual = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert expected == actual
