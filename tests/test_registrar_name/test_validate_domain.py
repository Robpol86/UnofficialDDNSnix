#!/usr/bin/env python2.6
import textwrap
import pytest
import time
from tests.test_registrar_name.test_request_json import initialize_simulation


def test_validate_domain_candidates_none(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2]}'
    json = "{u'bar': [u'baz', None, 1.0, 2], u'result': {u'message': u'Command Successful', u'code': 100}}"
    url = "http://127.0.0.1/domain/list"
    expected_exc = "Domain not registered to this registrar's account."
    stdout_expected = textwrap.dedent("""\
        Method validate_domain start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        """.format(url=url, response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.validate_domain Method validate_domain start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.validate_domain Response: {response}
        {ts} DEBUG    registrar_base.validate_domain JSON: {json}
        """.format(url=url, response=response, json=json, ts=timestamp))

    initialize_simulation(response)
    with open(log_file.name, 'r') as f:
        f.seek(0, 2)
        log_before_pos = f.tell()
    with pytest.raises(session.RegistrarException) as e:
        session.validate_domain()
    assert expected_exc == str(e.value)

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual


def test_validate_domain_candidates_error(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"domains":{"example.com":0,"com":0}}'
    json = "{u'domains': {u'com': 0, u'example.com': 0}, u'result': {u'message': u'Command Successful', u'code': 100}}"
    url = "http://127.0.0.1/domain/list"
    stdout_expected = textwrap.dedent("""\
        Method validate_domain start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        """.format(url=url, response=response, json=json))
    stderr_expected = "Cannot figure out main domain: [u'com', u'example.com']\n"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.validate_domain Method validate_domain start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.validate_domain Response: {response}
        {ts} DEBUG    registrar_base.validate_domain JSON: {json}
        {ts} ERROR    registrar_base.validate_domain Cannot figure out main domain: [u'com', u'example.com']
        """.format(url=url, response=response, json=json, ts=timestamp))

    initialize_simulation(response)
    with open(log_file.name, 'r') as f:
        f.seek(0, 2)
        log_before_pos = f.tell()
    with pytest.raises(ValueError):
        session.validate_domain()

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual


# noinspection PyProtectedMember
def test_validate_domain_success_sub(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"domains":{"example.com":{"tld":"com"},"example.info":{"tld":"info"}}}'
    json = "{u'domains': {u'example.info': {u'tld': u'info'}, u'example.com': {u'tld': u'com'}}, u'result': {u'message': u'Command Successful', u'code': 100}}"
    url = "http://127.0.0.1/domain/list"
    expected_result = "example.com"
    stdout_expected = textwrap.dedent("""\
        Method validate_domain start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        Method validate_domain end.
        """.format(url=url, response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.validate_domain Method validate_domain start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.validate_domain Response: {response}
        {ts} DEBUG    registrar_base.validate_domain JSON: {json}
        {ts} DEBUG    registrar_base.validate_domain Method validate_domain end.
        """.format(url=url, response=response, json=json, ts=timestamp))

    initialize_simulation(response)
    with open(log_file.name, 'r') as f:
        f.seek(0, 2)
        log_before_pos = f.tell()
    session.validate_domain()
    assert expected_result == session._main_domain

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual


# noinspection PyProtectedMember
def test_validate_domain_success_main(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"domains":{"example.com":{"tld":"com"},"example.info":{"tld":"info"}}}'
    json = "{u'domains': {u'example.info': {u'tld': u'info'}, u'example.com': {u'tld': u'com'}}, u'result': {u'message': u'Command Successful', u'code': 100}}"
    url = "http://127.0.0.1/domain/list"
    expected_result = "example.info"
    session.config['domain'] = "example.info"
    stdout_expected = textwrap.dedent("""\
        Method validate_domain start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        Method validate_domain end.
        """.format(url=url, response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.validate_domain Method validate_domain start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.validate_domain Response: {response}
        {ts} DEBUG    registrar_base.validate_domain JSON: {json}
        {ts} DEBUG    registrar_base.validate_domain Method validate_domain end.
        """.format(url=url, response=response, json=json, ts=timestamp))

    initialize_simulation(response)
    with open(log_file.name, 'r') as f:
        f.seek(0, 2)
        log_before_pos = f.tell()
    session.validate_domain()
    assert expected_result == session._main_domain

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual