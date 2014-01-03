#!/usr/bin/env python2.6
import textwrap
import pytest
import time
from tests.test_registrar_name.test_request_json import initialize_simulation


def _heavy_lifting(response, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected):
    initialize_simulation(response)
    with open(log_file.name, 'r') as f:
        f.seek(0, 2)
        log_before_pos = f.tell()
    with pytest.raises(session.RegistrarException) as e:
        session.get_current_ip()
    assert expected_exc == str(e.value)

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual


def test_get_current_ip_missing_json_key(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2]}'
    json = "{u'bar': [u'baz', None, 1.0, 2], u'result': {u'message': u'Command Successful', u'code': 100}}"
    expected_exc = "'client_ip' not in JSON."
    stdout_expected = textwrap.dedent("""\
        Method get_current_ip start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        """.format(url="http://127.0.0.1/hello", response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.get_current_ip  Method get_current_ip start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.get_current_ip  Response: {response}
        {ts} DEBUG    registrar_base.get_current_ip  JSON: {json}
        """.format(url="http://127.0.0.1/hello", response=response, json=json, ts=timestamp))
    _heavy_lifting(response, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_get_current_ip_missing_json_value(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2], "client_ip":""}'
    json = "{u'client_ip': u'', u'bar': [u'baz', None, 1.0, 2], u'result': {u'message': u'Command Successful', u'code': 100}}"
    expected_exc = "'client_ip' is not an IP address."
    stdout_expected = textwrap.dedent("""\
        Method get_current_ip start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        """.format(url="http://127.0.0.1/hello", response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.get_current_ip  Method get_current_ip start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.get_current_ip  Response: {response}
        {ts} DEBUG    registrar_base.get_current_ip  JSON: {json}
        """.format(url="http://127.0.0.1/hello", response=response, json=json, ts=timestamp))
    _heavy_lifting(response, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_get_current_ip_invalid_json_value(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2], "client_ip":"127..0.1"}'
    json = "{u'client_ip': u'127..0.1', u'bar': [u'baz', None, 1.0, 2], u'result': {u'message': u'Command Successful', u'code': 100}}"
    expected_exc = "'client_ip' is not an IP address."
    stdout_expected = textwrap.dedent("""\
        Method get_current_ip start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        """.format(url="http://127.0.0.1/hello", response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.get_current_ip  Method get_current_ip start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.get_current_ip  Response: {response}
        {ts} DEBUG    registrar_base.get_current_ip  JSON: {json}
        """.format(url="http://127.0.0.1/hello", response=response, json=json, ts=timestamp))
    _heavy_lifting(response, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_get_current_ip_success(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"service":"Name.com API Test Server","server_date":"2013-12-28 04:46:38","version":"2.0","language":"en","client_ip":"127.0.0.1"}'
    json = "{u'client_ip': u'127.0.0.1', u'service': u'Name.com API Test Server', u'language': u'en', u'version': u'2.0', u'result': {u'message': u'Command Successful', u'code': 100}, u'server_date': u'2013-12-28 04:46:38'}"
    expected_ip = "127.0.0.1"
    stdout_expected = textwrap.dedent("""\
        Method get_current_ip start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        Method get_current_ip end.
        """.format(url="http://127.0.0.1/hello", response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.get_current_ip  Method get_current_ip start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.get_current_ip  Response: {response}
        {ts} DEBUG    registrar_base.get_current_ip  JSON: {json}
        {ts} DEBUG    registrar_base.get_current_ip  Method get_current_ip end.
        """.format(url="http://127.0.0.1/hello", response=response, json=json, ts=timestamp))

    initialize_simulation(response)
    with open(log_file.name, 'r') as f:
        f.seek(0, 2)
        log_before_pos = f.tell()
    session.get_current_ip()
    assert expected_ip == session.current_ip

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual