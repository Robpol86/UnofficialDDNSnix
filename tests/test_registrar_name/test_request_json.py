#!/usr/bin/env python2.6
import StringIO
import textwrap
import urllib2
import pytest
import time


# noinspection PyProtectedMember
def _heavy_lifting(url, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected):
    with open(log_file.name, 'r') as f:
        f.seek(0, 2)
        log_before_pos = f.tell()
    with pytest.raises(session.RegistrarException) as e:
        session._request_json(url)
    assert expected_exc == str(e.value)

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual


def initialize_simulation(data):
    """Creates a simulated HTTP handler for all urllib2 operations, mimicking a web server."""
    class SimulatedHTTPHandler(urllib2.HTTPHandler):
        def http_open(self, req):
            if '127.0.0.1' not in req.get_full_url():
                # Only simulate if trying to hit localhost.
                return urllib2.HTTPHandler.http_open(self, req)
            resp = urllib2.addinfourl(StringIO.StringIO(data), "Simulation", req.get_full_url())
            resp.code = 200
            resp.msg = "OK"
            return resp

    urllib2.install_opener(urllib2.build_opener(SimulatedHTTPHandler))


def test_request_json_live_dns_unresolvable_timeout(session, log_file, capsys):
    url = "https://api.namse.com/api/hello"
    expected_exc = "Connection to %s timed out." % url
    stdout_expected = textwrap.dedent("""\
        Opening connection to {url}
        """.format(url=url))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        """.format(url=url, ts=timestamp))
    _heavy_lifting(url, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_request_json_live_dns_unresolvable_instant(session, log_file, capsys):
    url = "http://test29582757.com/index.html"
    expected_exc = "Connection to %s failed, DNS resolution failure." % url
    stdout_expected = textwrap.dedent("""\
        Opening connection to {url}
        """.format(url=url))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        """.format(url=url, ts=timestamp))
    _heavy_lifting(url, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_request_json_live_http_port_closed(session, log_file, capsys):
    url = "http://localhost:18722/index.html"  # Random port number.
    expected_exc = "Connection to %s refused." % url
    stdout_expected = textwrap.dedent("""\
        Opening connection to {url}
        """.format(url=url))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        """.format(url=url, ts=timestamp))
    _heavy_lifting(url, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_request_json_live_http_not_200(session, log_file, capsys):
    url = "https://api.name.com/api/404"
    expected_exc = "%s returned HTTP 404: HTTP Error 404: Not Found" % url
    stdout_expected = textwrap.dedent("""\
        Opening connection to {url}
        """.format(url=url))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        """.format(url=url, ts=timestamp))
    _heavy_lifting(url, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_request_json_simulated_http_not_json(session, log_file, capsys):
    response = "<body>This isn't JSON</body>"
    url = 'http://127.0.0.1'
    expected_exc = "Invalid JSON."
    initialize_simulation(response)
    stdout_expected = textwrap.dedent("""\
        Opening connection to {url}
        Response: {response}
        """.format(url=url, response=response))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base._request_json   Response: {response}
        """.format(url=url, response=response, ts=timestamp))
    _heavy_lifting(url, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_request_json_simulated_http_json_not_dict(session, log_file, capsys):
    response = '["foo", {"bar":["baz", null, 1.0, 2]}]'
    json = "[u'foo', {u'bar': [u'baz', None, 1.0, 2]}]"
    url = 'http://127.0.0.1'
    expected_exc = "Unexpected JSON format. Expected top-level to be a dictionary."
    initialize_simulation(response)
    stdout_expected = textwrap.dedent("""\
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        """.format(url=url, response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_name._request_json   Response: {response}
        {ts} DEBUG    registrar_name._request_json   JSON: {json}
        """.format(url=url, response=response, json=json, ts=timestamp))
    _heavy_lifting(url, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


def test_request_json_simulated_json_not_code_100(session, log_file, capsys):
    response = '{"bar":["baz", null, 1.0, 2]}'
    json = "{u'bar': [u'baz', None, 1.0, 2]}"
    url = 'http://127.0.0.1'
    expected_exc = "API returned an error."
    initialize_simulation(response)
    stdout_expected = textwrap.dedent("""\
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        """.format(url=url, response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_name._request_json   Response: {response}
        {ts} DEBUG    registrar_name._request_json   JSON: {json}
        """.format(url=url, response=response, json=json, ts=timestamp))
    _heavy_lifting(url, log_file, session, expected_exc, capsys, stdout_expected, stderr_expected, log_expected)


# noinspection PyProtectedMember
def test_request_json_simulated_success(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"records":[]}'
    url = 'http://127.0.0.1'
    expected_return = session.Payload(url, url, None, response)
    expected_return.parse()
    expected_json = {u'records': [], u'result': {u'message': u'Command Successful', u'code': 100}}
    initialize_simulation(response)
    stdout_expected = textwrap.dedent("""\
        Opening connection to {url}
        """.format(url=url))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        """.format(url=url, ts=timestamp))

    with open(log_file.name, 'r') as f:
        f.seek(0, 2)
        log_before_pos = f.tell()
    s = session._request_json(url)
    assert expected_return == s
    assert expected_json == s.json

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual