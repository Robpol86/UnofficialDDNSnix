#!/usr/bin/env python2.6
import textwrap
import time
import sys
from UnofficialDDNS import decider
from tests.test_registrar_name.test_request_json import initialize_simulation


def _heavy_lifting(response, log_file, session, expected_ips, capsys, stdout_expected, stderr_expected, log_expected):
    initialize_simulation(response)
    with open(log_file.name, 'r') as f:
        f.seek(0, 2)
        log_before_pos = f.tell()
    session.get_records()
    assert expected_ips == session.recorded_ips
    decider(session)

    stdout_actual, stderr_actual = capsys.readouterr()
    assert stdout_expected == stdout_actual
    assert stderr_expected == stderr_actual

    with open(log_file.name, 'r') as f:
        f.seek(log_before_pos)
        log_actual = f.read(10240)
    assert log_expected == log_actual


def test_no_records(session, log_file, capsys):
    response = '{"result":{"code":100,"message":"Command Successful"},"records":[]}'
    json = "{u'records': [], u'result': {u'message': u'Command Successful', u'code': 100}}"
    expected_ips = []
    stdout_expected = textwrap.dedent("""\
        Method get_records start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        Method get_records end.
        Creating A record.
        New Record
        """.format(url='http://127.0.0.1/dns/list/example.com', response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.get_records     Method get_records start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.get_records     Response: {response}
        {ts} DEBUG    registrar_base.get_records     JSON: {json}
        {ts} DEBUG    registrar_base.get_records     Method get_records end.
        {ts} INFO     UnofficialDDNS.decider         Creating A record.
        {ts} DEBUG    root                           New Record
        """.format(url='http://127.0.0.1/dns/list/example.com', response=response, json=json, ts=timestamp))
    _heavy_lifting(response, log_file, session, expected_ips, capsys, stdout_expected, stderr_expected, log_expected)


def test_unrelated_records(session, log_file, capsys):
    """When the main domain, targeted subdomain, and other subdomains have many non A/CNAME records which we should ignore."""
    pass


def test_matching_unrelated_and_nonmatching_a_and_cname_records(session, log_file, capsys):
    """A and CNAME records on unrelated subdomains, and non A/CNAME records on the targeted subdomain."""
    pass


def test_matching_a_and_cname_with_incorrect_content(session, log_file, capsys):
    """A and CNAME records on the matching/targeted subdomain, but set to some other IP address."""
    response = '{"result":{"code":100,"message":"Command Successful"},"records":[{"record_id":"482702","name":"sub.example.com","type":"A","content":"192.168.1.1","ttl":"300","create_date":"2013-12-30 01:04:20","priority":"10"},{"record_id":"94726","name":"sub.example.com","type":"CNAME","content":"test.example.com","ttl":"300","create_date":"2013-12-30 01:26:15"},{"record_id":"8746285","name":"sub.example.com","type":"A","content":"192.168.11.1","ttl":"300","create_date":"2013-12-30 01:26:42","priority":"10"}]}'
    json = "{u'records': [{u'priority': u'10', u'create_date': u'2013-12-30 01:04:20', u'name': u'sub.example.com', u'content': u'192.168.1.1', u'ttl': u'300', u'record_id': u'482702', u'type': u'A'}, {u'create_date': u'2013-12-30 01:26:15', u'name': u'sub.example.com', u'content': u'test.example.com', u'ttl': u'300', u'record_id': u'94726', u'type': u'CNAME'}, {u'priority': u'10', u'create_date': u'2013-12-30 01:26:42', u'name': u'sub.example.com', u'content': u'192.168.11.1', u'ttl': u'300', u'record_id': u'8746285', u'type': u'A'}], u'result': {u'message': u'Command Successful', u'code': 100}}"
    expected_ips = [
        session.Record('482702', 'A', 'sub.example.com', '192.168.1.1'),
        session.Record('94726', 'CNAME', 'sub.example.com', 'test.example.com'),
        session.Record('8746285', 'A', 'sub.example.com', '192.168.11.1'),
    ]
    stdout_expected = textwrap.dedent("""\
        Method get_records start.
        Opening connection to {url}
        Response: {response}
        JSON: {json}
        Method get_records end.
        Creating A record.
        New Record
        Removing old/incorrect record ID 482702 with value 192.168.1.1.
        Delete Record 482702
        Removing old/incorrect record ID 94726 with value test.example.com.
        Delete Record 94726
        Removing old/incorrect record ID 8746285 with value 192.168.11.1.
        Delete Record 8746285
        """.format(url='http://127.0.0.1/dns/list/example.com', response=response, json=json))
    stderr_expected = ''
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    log_expected = textwrap.dedent("""\
        {ts} DEBUG    registrar_base.get_records     Method get_records start.
        {ts} DEBUG    registrar_base._request_json   Opening connection to {url}
        {ts} DEBUG    registrar_base.get_records     Response: {response}
        {ts} DEBUG    registrar_base.get_records     JSON: {json}
        {ts} DEBUG    registrar_base.get_records     Method get_records end.
        {ts} INFO     UnofficialDDNS.decider         Creating A record.
        {ts} DEBUG    root                           New Record
        {ts} INFO     UnofficialDDNS.decider         Removing old/incorrect record ID 482702 with value 192.168.1.1.
        {ts} DEBUG    root                           Delete Record 482702
        {ts} INFO     UnofficialDDNS.decider         Removing old/incorrect record ID 94726 with value test.example.com.
        {ts} DEBUG    root                           Delete Record 94726
        {ts} INFO     UnofficialDDNS.decider         Removing old/incorrect record ID 8746285 with value 192.168.11.1.
        {ts} DEBUG    root                           Delete Record 8746285
        """.format(url='http://127.0.0.1/dns/list/example.com', response=response, json=json, ts=timestamp))
    _heavy_lifting(response, log_file, session, expected_ips, capsys, stdout_expected, stderr_expected, log_expected)


def test_matching_cname_with_correct_content(session, log_file, capsys):
    """CNAME record on the targeted subdomain, set to the current IP. Should be removed since we want A records instead."""
    pass


def test_matching_a_multiple_incorrect(session, log_file, capsys):
    """Multiple A records on the same targeted subdomain, all set to different incorrect IPs. All should be purged."""
    pass


def test_matching_a_multiple_partially_incorrect(session, log_file, capsys):
    """Multiple A records, one of them is set with the current IP, but others arent. Purge only those."""
    pass


def test_matching_a_multiple_correct(session, log_file, capsys):
    """Multiple A records, all identical, all set to the current IP. Purge all but one."""
    pass


def test_matching_a_single_correct(session, log_file, capsys):
    """Single A records, already set to the current IP. Do nothing."""
    pass