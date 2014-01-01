#!/usr/bin/env python2.6
import StringIO
import logging
import logging.config
import sys
import tempfile
import textwrap
import unittest
import urllib2
import time
import libs
from UnofficialDDNS import decider
from registrar_name import RegistrarName

# TODO: test create_record.
def initialize_simulation(data):
    """Creates a simulated HTTP handler for all urllib2 operations, mimicking a web server."""
    s = StringIO.StringIO(data)

    class SimulatedHTTPHandler(urllib2.HTTPHandler):
        def http_open(self, req):
            resp = urllib2.addinfourl(s, "Simulation", req.get_full_url())
            resp.code = 200
            resp.msg = "OK"
            return resp

    urllib2.install_opener(urllib2.build_opener(SimulatedHTTPHandler))


# noinspection PyProtectedMember
class TestRegistrarNameBase(unittest.TestCase):

    success = """{"result":{"code":100,"message":"Command Successful"},"""

    def setUp(self):
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        self.log_file = tempfile.NamedTemporaryFile()
        self.maxDiff = None
        self.session = RegistrarName(dict(user="USER", passwd="PASSWD", domain="sub.example.com"))
        self.session._url_base = "http://127.0.0.1"
        self.session._url_get_current_ip = self.session._url_base + "/hello"
        self.session._url_authenticate = self.session._url_base + "/login"
        self.session._url_get_main_domain = self.session._url_base + "/domain/list"
        self.session._url_get_records_prefix = self.session._url_base + "/dns/list"
        self.session._url_delete_record_prefix = self.session._url_base + "/dns/delete"
        self.session._url_create_record_prefix = self.session._url_base + "/dns/create"
        self.session._url_logout = self.session._url_base + "/logout"
        with libs.LoggingSetup(True, self.log_file.name, False) as cm:
            logging.config.fileConfig(cm.config)  # Setup logging.

    def tearDown(self):
        self.log_file.close()


# noinspection PyProtectedMember
class TestRegistrarNameLiveRequestJSON(TestRegistrarNameBase):
    def test_dns_unresolvable_timeout(self):
        url = "https://api.namse.com/api/hello"
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session._request_json(url)
        self.assertEqual(cm.exception.message, "Connection to %s timed out." % url)

    def test_dns_unresolvable_instant(self):
        url = "http://test29582757.com/index.html"
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session._request_json(url)
        self.assertEqual(cm.exception.message, "Connection to %s failed, DNS resolution failure." % url)

    def test_http_port_closed(self):
        url = "http://127.0.0.1:18722/index.html"  # Random port number.
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session._request_json(url)
        self.assertEqual(cm.exception.message, "Connection to %s refused." % url)

    def test_http_not_200(self):
        url = "https://api.name.com/api/404"
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session._request_json(url)
        self.assertEqual(cm.exception.message, "%s returned HTTP 404: HTTP Error 404: Not Found" % url)


# noinspection PyProtectedMember
class TestRegistrarNameSimulatedRequestJSON(TestRegistrarNameBase):
    def test_http_not_json(self):
        initialize_simulation("<body>This isn't JSON</body>")
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session._request_json(self.session._url_base)
        self.assertEqual(cm.exception.message, "Invalid JSON.")

    def test_http_json_not_dict(self):
        initialize_simulation('["foo", {"bar":["baz", null, 1.0, 2]}]')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session._request_json(self.session._url_base)
        self.assertEqual(cm.exception.message, "Unexpected JSON format. Expected top-level to be a dictionary.")

    def test_http_json_not_code_100(self):
        initialize_simulation('{"bar":["baz", null, 1.0, 2]}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session._request_json(self.session._url_base)
        self.assertEqual(cm.exception.message, "API returned an error.")


class TestRegistrarNameSimulatedGetCurrentIP(TestRegistrarNameBase):
    def test_get_current_ip_missing_json_key(self):
        initialize_simulation(self.success + '"bar":["baz", null, 1.0, 2]}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.get_current_ip()
        self.assertEqual(cm.exception.message, "'client_ip' not in JSON.")

    def test_get_current_ip_missing_json_value(self):
        initialize_simulation(self.success + '"bar":["baz", null, 1.0, 2], "client_ip":""}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.get_current_ip()
        self.assertEqual(cm.exception.message, "'client_ip' is not an IP address.")

    def test_get_current_ip_invalid_json_value(self):
        initialize_simulation(self.success + '"bar":["baz", null, 1.0, 2], "client_ip":"127..0.1"}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.get_current_ip()
        self.assertEqual(cm.exception.message, "'client_ip' is not an IP address.")

    def test_get_current_ip_success(self):
        data = self.success + """"service":"Name.com API Test Server",""" + \
            """"server_date":"2013-12-28 04:46:38","version":"2.0","language":"en","client_ip":"127.0.0.1"}"""
        initialize_simulation(data)
        self.session.get_current_ip()
        self.assertEqual(self.session.current_ip, "127.0.0.1")


# noinspection PyProtectedMember
class TestRegistrarNameSimulatedAuthenticate(TestRegistrarNameBase):
    def test_authenticate_missing_json_key(self):
        initialize_simulation(self.success + '"bar":["baz", null, 1.0, 2]}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.authenticate()
        self.assertEqual(cm.exception.message, "'session_token' not in JSON.")

    def test_authenticate_missing_json_value(self):
        initialize_simulation(self.success + '"bar":["baz", null, 1.0, 2], "session_token":""}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.authenticate()
        self.assertEqual(cm.exception.message, "'session_token' is invalid.")

    def test_authenticate_invalid_json_value(self):
        initialize_simulation(self.success + '"bar":["baz", null, 1.0, 2], "session_token":"127..0.1"}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.authenticate()
        self.assertEqual(cm.exception.message, "'session_token' is invalid.")

    def test_authenticate_bad_credentials(self):
        data = """{"result":{"code":221,"message":"Authorization Error - Username Or Ip Token Invalid"}}"""
        initialize_simulation(data)
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.authenticate()
        self.assertEqual(cm.exception.message, "Authorization Error or invalid username and/or password.")

    def test_authenticate_success(self):
        data = self.success + '"session_token":"2352e5c5a0127d2155377664a5543f22a70be187"}'
        initialize_simulation(data)
        self.session.authenticate()
        self.assertEqual(self.session._session_token, "2352e5c5a0127d2155377664a5543f22a70be187")


# noinspection PyProtectedMember
class TestRegistrarNameSimulatedValidateDomain(TestRegistrarNameBase):
    def test_validate_domain_candidates_none(self):
        initialize_simulation(self.success + '"bar":["baz", null, 1.0, 2]}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.validate_domain()
        self.assertEqual(cm.exception.message, "Domain not registered to this registrar's account.")

    def test_validate_domain_candidates_error(self):
        initialize_simulation(self.success + '"domains":{"example.com":0,"com":0}}')
        with self.assertRaises(ValueError):
            self.session.validate_domain()

    def test_validate_domain_success_sub(self):
        data = self.success + '"domains":{"example.com":{"tld":"com"},"example.info":{"tld":"info"}}}'
        initialize_simulation(data)
        self.session.validate_domain()
        self.assertEqual(self.session._main_domain, "example.com")

    def test_validate_domain_success_main(self):
        data = self.success + '"domains":{"example.com":{"tld":"com"},"example.info":{"tld":"info"}}}'
        initialize_simulation(data)
        self.session.config['domain'] = "example.info"
        self.session.validate_domain()
        self.assertEqual(self.session._main_domain, "example.info")


class TestRegistrarNameSimulatedGetRecordsDecider(TestRegistrarNameBase):
    def setUp(self):
        super(TestRegistrarNameSimulatedGetRecordsDecider, self).setUp()
        self.session._main_domain = "example.com"
        self.session.current_ip = "127.0.0.1"
        self.session.create_record = lambda: logging.debug("New Record")
        self.session.delete_record = lambda record: logging.debug("Delete Record %s" % record)

    def test_no_records(self):
        response = '{"result":{"code":100,"message":"Command Successful"},"records":[]}'
        json = "{u'records': [], u'result': {u'message': u'Command Successful', u'code': 100}}"
        initialize_simulation(response)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.session.get_records()
        self.assertEqual(self.session.recorded_ips, [])
        decider(self.session)

        stdout_actual = sys.stdout.getvalue()
        stderr_actual = sys.stderr.getvalue()
        stdout_expected = textwrap.dedent("""\
            Method get_records start.
            Response: {response}
            JSON: {json}
            Method get_records end.
            Creating A record.
            New Record
            """.format(response=response, json=json))
        stderr_expected = ''
        self.assertMultiLineEqual(stdout_expected, stdout_actual)
        self.assertMultiLineEqual(stderr_expected, stderr_actual)

        log_actual = self.log_file.read(1024)
        log_expected = textwrap.dedent("""\
            {ts} DEBUG    registrar_base.get_records     Method get_records start.
            {ts} DEBUG    registrar_base.get_records     Response: {response}
            {ts} DEBUG    registrar_base.get_records     JSON: {json}
            {ts} DEBUG    registrar_base.get_records     Method get_records end.
            {ts} INFO     UnofficialDDNS.decider         Creating A record.
            {ts} DEBUG    root                           New Record
            """.format(response=response, json=json, ts=timestamp))
        self.assertMultiLineEqual(log_expected, log_actual)
"""
    def test_get_records_mx_only(self):
        data = self.success + '"records":[{"record_id":"275192602","name":"sub.example.com","type":"MX",' + \
            '"content":"127.0.0.1","ttl":"300","create_date":"2013-12-30 01:03:57","priority":"10"}]}'
        initialize_simulation(data)
        self.session.get_records()
        self.assertEqual(self.session.recorded_ips, [])

    def test_get_records_a_and_mx(self):
        data = self.success + '"records":[{"record_id":"275192602","name":"sub.example.com","type":"MX",' + \
            '"content":"127.0.0.1","ttl":"300","create_date":"2013-12-30 01:03:57","priority":"10"},' + \
            '{"record_id":"175192602","name":"sub.example.com","type":"A","content":"192.168.0.1","ttl":"300",' + \
            '"create_date":"2013-12-30 01:04:20","priority":"10"}]}'
        expected = [self.session.Record('175192602', 'A', 'sub.example.com', '192.168.0.1'), ]
        initialize_simulation(data)
        self.session.get_records()
        self.assertEqual(self.session.recorded_ips, expected)

    def test_get_records_a_and_cname(self):
        data = self.success + '"records":[{"record_id":"275192602","name":"sub.example.com","type":"A",' + \
            '"content":"127.0.0.1","ttl":"300","create_date":"2013-12-30 01:04:20","priority":"10"},' + \
            '{"record_id":"175192602","name":"sub.example.com","type":"CNAME","content":"test.example.com",' + \
            '"ttl":"300","create_date":"2013-12-30 01:26:15"}]}'
        expected = [self.session.Record('175192602', 'A', 'test.example.com', '192.168.0.1'), ]
        initialize_simulation(data)
        self.session.get_records()
        self.assertEqual(self.session.recorded_ips, {'175192602': 'test.example.com', '275192602': '127.0.0.1'})

    def test_get_records_multiple_a(self):
        data = self.success + '"records":[{"record_id":"275192602","name":"sub.example.com","type":"A",' + \
            '"content":"127.0.0.1","ttl":"300","create_date":"2013-12-30 01:11:10","priority":"10"},' + \
            '{"record_id":"175192602","name":"sub.example.com","type":"A","content":"192.168.0.1","ttl":"300",' + \
            '"create_date":"2013-12-30 01:04:20","priority":"10"}]}'
        initialize_simulation(data)
        self.session.get_records()
        self.assertEqual(self.session.recorded_ips, {'175192602': '192.168.0.1', '275192602': '127.0.0.1'})

    def test_get_records_single_a(self):
        data = self.success + '"records":[{"record_id":"275192602","name":"sub.example.com","type":"A",' + \
            '"content":"127.0.0.1","ttl":"300","create_date":"2013-12-29 22:18:25","priority":"10"}]}'
        initialize_simulation(data)
        self.session.get_records()
        self.assertEqual(self.session.recorded_ips, {'275192602': '127.0.0.1'})
"""

if __name__ == "__main__":
    unittest.main(buffer=True)
