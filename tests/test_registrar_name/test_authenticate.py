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
        session.authenticate()
    assert expected_exc == str(e.value)

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual


def test_authenticate_missing_json_key(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2]}'
    json = "{u'bar': [u'baz', None, 1.0, 2], u'result': {u'message': u'Command Successful', u'code': 100}}"
    expected_exc = "'session_token' not in JSON."
    stdout_expected = textwrap.dedent("""\
        Method authenticate start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        """.format(url="http://127.0.0.1/login", response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.authenticate    Method authenticate start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.authenticate    Response: {response}
        {ts} DEBUG    registrar_base.authenticate    JSON: {json}
        """.format(url="http://127.0.0.1/login", response=response, json=json, ts=timestamp))
    _heavy_lifting(response, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_authenticate_missing_json_value(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2], "session_token":""}'
    json = "{u'bar': [u'baz', None, 1.0, 2], u'result': {u'message': u'Command Successful', u'code': 100}, u'session_token': u''}"
    expected_exc = "'session_token' is invalid."
    stdout_expected = textwrap.dedent("""\
        Method authenticate start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        """.format(url="http://127.0.0.1/login", response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.authenticate    Method authenticate start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.authenticate    Response: {response}
        {ts} DEBUG    registrar_base.authenticate    JSON: {json}
        """.format(url="http://127.0.0.1/login", response=response, json=json, ts=timestamp))
    _heavy_lifting(response, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_authenticate_invalid_json_value(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2], "session_token":"127..0.1"}'
    json = "{u'bar': [u'baz', None, 1.0, 2], u'result': {u'message': u'Command Successful', u'code': 100}, u'session_token': u'127..0.1'}"
    expected_exc = "'session_token' is invalid."
    stdout_expected = textwrap.dedent("""\
        Method authenticate start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        """.format(url="http://127.0.0.1/login", response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.authenticate    Method authenticate start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.authenticate    Response: {response}
        {ts} DEBUG    registrar_base.authenticate    JSON: {json}
        """.format(url="http://127.0.0.1/login", response=response, json=json, ts=timestamp))
    _heavy_lifting(response, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_authenticate_bad_credentials(session, log_file, capsys):
    response = '{"result":{"code":221,"message":"Authorization Error - Username Or Ip Token Invalid"}}'
    json = "{u'result': {u'message': u'Authorization Error - Username Or Ip Token Invalid', u'code': 221}}"
    expected_exc = "Authorization Error or invalid username and/or password."
    stdout_expected = textwrap.dedent("""\
        Method authenticate start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        """.format(url="http://127.0.0.1/login", response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.authenticate    Method authenticate start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_name._request_json   Response: {response}
        {ts} DEBUG    registrar_name._request_json   JSON: {json}
        """.format(url="http://127.0.0.1/login", response=response, json=json, ts=timestamp))
    _heavy_lifting(response, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


# noinspection PyProtectedMember
def test_authenticate_success(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"session_token":"2352e5c5a0127d2155377664a5543f22a70be187"}'
    json = "{u'client_ip': u'127.0.0.1', u'service': u'Name.com API Test Server', u'language': u'en', u'version': u'2.0', u'result': {u'message': u'Command Successful', u'code': 100}, u'server_date': u'2013-12-28 04:46:38'}"
    expected_token = "2352e5c5a0127d2155377664a5543f22a70be187"
    stdout_expected = textwrap.dedent("""\
        Method authenticate start.
        Opening connection to {url}
        Method authenticate end.
        """.format(url="http://127.0.0.1/login", response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.authenticate    Method authenticate start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.authenticate    Method authenticate end.
        """.format(url="http://127.0.0.1/login", response=response, json=json, ts=timestamp))

    initialize_simulation(response)
    with open(log_file.name, 'r') as f:
        f.seek(0, 2)
        log_before_pos = f.tell()
    session.authenticate()
    assert expected_token == session._session_token

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual