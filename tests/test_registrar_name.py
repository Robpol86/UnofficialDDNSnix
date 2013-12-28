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
        self.session = RegistrarName(dict())
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

    def test_get_current_ip_missing_json_key(self):
        initialize_simulation('["foo", {"bar":["baz", null, 1.0, 2]}]')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.get_current_ip()
        self.assertEqual(cm.exception.message, "'client_ip' not in JSON.")

    def test_get_current_ip_missing_json_value(self):
        initialize_simulation('{"bar":["baz", null, 1.0, 2], "client_ip":""}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.get_current_ip()
        self.assertEqual(cm.exception.message, "'client_ip' is not an IP address.")

    def test_get_current_ip_invalid_json_value(self):
        initialize_simulation('{"bar":["baz", null, 1.0, 2], "client_ip":"127..0.1"}')
        with self.assertRaises(RegistrarName.RegistrarException) as cm:
            self.session.get_current_ip()
        self.assertEqual(cm.exception.message, "'client_ip' is not an IP address.")

    def test_get_current_ip_success(self):
        initialize_simulation('{"bar":["baz", null, 1.0, 2], "client_ip":"127.0.0.1"}')
        self.session.get_current_ip()
        self.assertEqual(self.session.current_ip, "127.0.0.1")


if __name__ == "__main__":
    unittest.main(buffer=True)
