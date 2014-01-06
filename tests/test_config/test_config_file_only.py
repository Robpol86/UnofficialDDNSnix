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
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Unable to read config file %s, invalid data." % config_file.name == str(e.value)


def test_config_file_only_with_nonexistent_file():
    argv = ['-c', '/tmp/doesNotExist.28520']
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Config file /tmp/doesNotExist.28520 does not exist, not a file, or no permission." == str(e.value)


def test_config_file_only_with_no_read_permissions():
    argv = ['-c', '/etc/sudoers']
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Unable to read config file /etc/sudoers." == str(e.value)


def test_config_file_only_with_directory_instead_of_file():
    argv = ['-c', '/etc']
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Config file /etc does not exist, not a file, or no permission." == str(e.value)


def test_config_file_only_with_invalid_text_data_not_yaml(config_file):
    config_file.write("daemon\n")
    config_file.flush()
    argv = ['-c', config_file.name]
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Config file %s contents didn't yield dict or not YAML: daemon" % config_file.name == str(e.value)


def test_config_file_only_with_invalid_text_data_not_yaml_big(config_file):
    config_file.write("""
        domain mydomain.com  # i am a comment
        user thisuser#comment
        #another comment
        passwd abc"
    """)
    config_file.flush()
    argv = ['-c', config_file.name]
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Config file %s contents not YAML formatted:" % config_file.name in str(e.value)


def test_config_file_only_with_invalid_text_data_unknown_option(config_file):
    config_file.write("test: true\n")
    config_file.flush()
    argv = ['-c', config_file.name]
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Unknown option test in config file %s." % config_file.name == str(e.value)


def test_config_file_only_with_invalid_text_data_unknown_value(config_file):
    config_file.write("daemon: unknown\n")
    config_file.flush()
    argv = ['-c', config_file.name]
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Config file option daemon must be True or False." == str(e.value)


def test_config_file_only_missing_log_value(config_file):
    config_file.write("domain: mydomain.com\nuser: thisuser\npasswd: abc\nlog: #True\n")
    config_file.flush()
    argv = ['-c', config_file.name]
    config = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert None == config['log']


def test_config_file_only_tab_character(config_file):
    config_file.write("domain: mydomain.com\nuser:\tthisuser\npasswd: abc")
    config_file.flush()
    argv = ['-c', config_file.name]
    with pytest.raises(libs.MultipleConfigSources.ConfigError) as e:
        libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert "Tab character found in config file %s. Must use spaces only!" % config_file.name == str(e.value)


def test_config_file_only_with_full_valid_data(config_file):
    config_file.write("domain: mydomain.com\nuser: thisuser\npasswd: abc")
    config_file.flush()
    argv = ['-c', config_file.name]
    expected = dict(log=None, daemon=False, verbose=False, interval=60, pid=None, quiet=False, version=False,
                    registrar='name.com', config=config_file.name, help=False,
                    user='thisuser', passwd='abc', domain='mydomain.com')
    actual = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert expected == actual


def test_config_file_only_with_full_valid_data_and_comments(config_file):
    config_file.write("""
        domain:    mydomain.com  # i am a comment
        user: thisuser #comment
        #another comment
        passwd: abc
    """)
    config_file.flush()
    argv = ['-c', config_file.name]
    expected = dict(log=None, daemon=False, verbose=False, interval=60, pid=None, quiet=False, version=False,
                    registrar='name.com', config=config_file.name, help=False,
                    user='thisuser', passwd='abc', domain='mydomain.com')
    actual = libs.get_config(docopt(uddns_doc, version=uddns_ver, argv=argv))
    assert expected == actual
