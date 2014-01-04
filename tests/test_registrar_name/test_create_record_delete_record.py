#!/usr/bin/env python2.6
import textwrap
import time
from tests.test_registrar_name.test_request_json import initialize_simulation


def _heavy_lifting(response, log_file, session, capsys, stdout_expected, stderr_expected, log_expected, delete):
    initialize_simulation(response)
    with open(log_file.name, 'r') as f:
        f.seek(0, 2)
        log_before_pos = f.tell()
    if delete:
        session.delete_record(delete)
    else:
        session.create_record()

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual


def test_create_record_sub(session, log_file, capsys):
    post = '{"priority": 10, "content": "127.0.0.1", "hostname": "sub", "type": "A", "ttl": 300}'
    response = '{"result":{"code":100,"message":"Command Successful"},"record_id":238454450,"name":"sub.example.com","type":"A","content":"127.0.0.1","ttl":300,"create_date":"2014-01-03 19:32:53","priority":10}'
    json = "{u'priority': 10, u'create_date': u'2014-01-03 19:32:53', u'name': u'sub.example.com', u'content': u'127.0.0.1', u'result': {u'message': u'Command Successful', u'code': 100}, u'ttl': 300, u'record_id': 238454450, u'type': u'A'}"
    url = 'http://127.0.0.1/dns/create/example.com'
    stdout_expected = textwrap.dedent("""\
        Method create_record start.
        Sending POST data: {post}
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        Method create_record end.
        """.format(url=url, response=response, json=json, post=post))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.create_record   Method create_record start.
        {ts} DEBUG    registrar_base.create_record   Sending POST data: {post}
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.create_record   Response: {response}
        {ts} DEBUG    registrar_base.create_record   JSON: {json}
        {ts} DEBUG    registrar_base.create_record   Method create_record end.
        """.format(url=url, response=response, json=json, post=post, ts=timestamp))
    _heavy_lifting(response, log_file, session, capsys, stdout_expected, stderr_expected, log_expected, None)


def test_create_record_main(session, log_file, capsys):
    post = '{"priority": 10, "content": "127.0.0.1", "hostname": ".", "type": "A", "ttl": 300}'
    response = '{"result":{"code":100,"message":"Command Successful"},"record_id":238454450,"name":"example.com","type":"A","content":"127.0.0.1","ttl":300,"create_date":"2014-01-03 19:32:53","priority":10}'
    json = "{u'priority': 10, u'create_date': u'2014-01-03 19:32:53', u'name': u'example.com', u'content': u'127.0.0.1', u'result': {u'message': u'Command Successful', u'code': 100}, u'ttl': 300, u'record_id': 238454450, u'type': u'A'}"
    url = 'http://127.0.0.1/dns/create/example.com'
    session.config['domain'] = 'example.com'
    stdout_expected = textwrap.dedent("""\
        Method create_record start.
        Sending POST data: {post}
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        Method create_record end.
        """.format(url=url, response=response, json=json, post=post))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.create_record   Method create_record start.
        {ts} DEBUG    registrar_base.create_record   Sending POST data: {post}
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.create_record   Response: {response}
        {ts} DEBUG    registrar_base.create_record   JSON: {json}
        {ts} DEBUG    registrar_base.create_record   Method create_record end.
        """.format(url=url, response=response, json=json, post=post, ts=timestamp))
    _heavy_lifting(response, log_file, session, capsys, stdout_expected, stderr_expected, log_expected, None)


def test_delete_record(session, log_file, capsys):
    post = '{"record_id": "12345226"}'
    response = '{"result":{"code":100,"message":"Command Successful"}}'
    json = "{u'result': {u'message': u'Command Successful', u'code': 100}}"
    url = 'http://127.0.0.1/dns/delete/example.com'
    stdout_expected = textwrap.dedent("""\
        Method delete_record start.
        Sending POST data: {post}
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        Method delete_record end.
        """.format(url=url, response=response, json=json, post=post))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.delete_record   Method delete_record start.
        {ts} DEBUG    registrar_base.delete_record   Sending POST data: {post}
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.delete_record   Response: {response}
        {ts} DEBUG    registrar_base.delete_record   JSON: {json}
        {ts} DEBUG    registrar_base.delete_record   Method delete_record end.
        """.format(url=url, response=response, json=json, post=post, ts=timestamp))
    _heavy_lifting(response, log_file, session, capsys, stdout_expected, stderr_expected, log_expected, "12345226")