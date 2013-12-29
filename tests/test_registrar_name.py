#!/usr/bin/env python2.6
from registrar_name import RegistrarName
import StringIO
import sys
import unittest
import urllib2


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
class TestRegistrarNameLive(unittest.TestCase):
    def setUp(self):
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        self.maxDiff = None
        self.session = RegistrarName(dict())

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
class TestRegistrarNameSimulated(unittest.TestCase):
    def setUp(self):
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
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

    def test_get_current_ip_missing_json_key(self):
        initialize_simulation('{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2]}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.get_current_ip()
        self.assertEqual(cm.exception.message, "'client_ip' not in JSON.")

    def test_get_current_ip_missing_json_value(self):
        initialize_simulation('{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2], "client_ip":""}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.get_current_ip()
        self.assertEqual(cm.exception.message, "'client_ip' is not an IP address.")

    def test_get_current_ip_invalid_json_value(self):
        initialize_simulation('{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2], "client_ip":"127..0.1"}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.get_current_ip()
        self.assertEqual(cm.exception.message, "'client_ip' is not an IP address.")

    def test_get_current_ip_success(self):
        data = """{"result":{"code":100,"message":"Command Successful"},"service":"Name.com API Test Server",""" + \
            """"server_date":"2013-12-28 04:46:38","version":"2.0","language":"en","client_ip":"127.0.0.1"}"""
        initialize_simulation(data)
        self.session.get_current_ip()
        self.assertEqual(self.session.current_ip, "127.0.0.1")

    def test_authenticate_missing_json_key(self):
        initialize_simulation('{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2]}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.authenticate()
        self.assertEqual(cm.exception.message, "'session_token' not in JSON.")

    def test_authenticate_missing_json_value(self):
        initialize_simulation('{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2], "session_token":""}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.authenticate()
        self.assertEqual(cm.exception.message, "'session_token' is invalid.")

    def test_authenticate_invalid_json_value(self):
        initialize_simulation('{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2], "session_token":"127..0.1"}')
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
        data = """{"result":{"code":100,"message":"Command Successful"},""" + \
            """"session_token":"2352e5c5a0127d2155377664a5543f22a70be187"}"""
        initialize_simulation(data)
        self.session.authenticate()
        self.assertEqual(self.session._session_token, "2352e5c5a0127d2155377664a5543f22a70be187")

    def test_validate_domain_candidates_none(self):
        initialize_simulation('{"result":{"code":100,"message":"Command Successful"},"bar":["baz", null, 1.0, 2]}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.validate_domain()
        self.assertEqual(cm.exception.message, "Domain not registered to this registrar's account.")

    def test_validate_domain_candidates_error(self):
        initialize_simulation('{"result":{"code":100,"message":"Command Successful"},"domains":{"example.com":0,"com":0}}')
        with self.assertRaises(ValueError):
            self.session.validate_domain()

    def test_validate_domain_success_sub(self):
        data = """{"result":{"code":100,"message":"Command Successful"},""" + \
            """"domains":{"example.com":{"tld":"com"},"example.info":{"tld":"info"}}}"""
        initialize_simulation(data)
        self.session.validate_domain()
        self.assertEqual(self.session._main_domain, "example.com")

    def test_validate_domain_success_main(self):
        data = """{"result":{"code":100,"message":"Command Successful"},""" + \
            """"domains":{"example.com":{"tld":"com"},"example.info":{"tld":"info"}}}"""
        initialize_simulation(data)
        self.session.config['domain'] = "example.info"
        self.session.validate_domain()
        self.assertEqual(self.session._main_domain, "example.info")


if __name__ == "__main__":
    unittest.main(buffer=True)
