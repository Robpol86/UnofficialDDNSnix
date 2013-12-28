#!/usr/bin/env python2.6
"""Base class for all registrars in UnofficialDDNSnix.
https://github.com/Robpol86/UnofficialDDNSnix
"""

import json
import logging
import re
import urllib2


class RegistrarBase(object):

    _url_base = None
    _url_get_current_ip = None
    _url_authenticate = None
    _url_get_main_domain = None
    _url_get_records_prefix = None
    _url_delete_record_prefix = None
    _url_create_record_prefix = None
    _url_logout = None

    def __init__(self, config):
        self.config = config
        self.current_ip = None
        self.recorded_ip = None
        self._main_domain = None
        self._session_token = None

    def __enter__(self):
        self.get_current_ip()
        self.authenticate()
        self.validate_domain()
        self.get_records()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.logout()
        self._session_token = None

    class RegistrarException(Exception):
        """Exception to be raised inside RegistrarBase and its derivatives when a handled error occurs."""
        pass

    def _request_json(self, url, post_data=None):
        """Handles HTTP connections and returns a JSON dictionary."""
        logger = logging.getLogger('%s._request_json' % self.__class__.__name__)
        logger.debug("Opening connection to %s" % url)
        request = urllib2.Request(url, post_data)
        if self._session_token:
            request.add_header('Api-Session-Token', self._session_token)

        # Attempt to make a connection.
        try:
            response = urllib2.urlopen(request, timeout=10)
        except urllib2.HTTPError as e:
            raise self.RegistrarException("%s returned HTTP %d: %s" % (url, e.code, e))
        except urllib2.URLError as e:
            if "error timed out" in str(e):
                raise self.RegistrarException("Connection to %s timed out." % url)
            elif "Connection refused" in str(e):
                raise self.RegistrarException("Connection to %s refused." % url)
            elif "nodename nor servname provided, or not known" in str(e):
                raise self.RegistrarException("Connection to %s failed, DNS resolution failure." % url)
            raise self.RegistrarException("URLError on %s: %s" % (url, e))

        # Validate the response.
        if url != response.geturl():
            logger.debug("Redirected from %s to %s." % (url, response.geturl()))
        if response.getcode() != 200:
            raise self.RegistrarException("%s returned HTTP %d." % (response.geturl(), response.getcode()))

        # Parse the response into a JSON dictionary.
        try:
            return json.load(response)
        except ValueError:
            response.fp.seek(0)
            logger.error("Invalid JSON: %s" % response.read())
            raise self.RegistrarException("Invalid JSON.")

    def get_current_ip(self):
        logger = logging.getLogger('%s.get_current_ip' % self.__class__.__name__)
        logger.debug("Method get_current_ip start.")
        data = self._request_json(self._url_get_current_ip)
        if 'client_ip' not in data:
            logger.error("Invalid JSON: %s" % data)
            raise self.RegistrarException("'client_ip' not in JSON.")
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", data['client_ip']):
            logger.error("Invalid JSON: %s" % data)
            raise self.RegistrarException("'client_ip' is not an IP address.")
        self.current_ip = data['client_ip']
        logger.debug("Method get_current_ip end.")

    def authenticate(self):
        logger = logging.getLogger('%s.authenticate' % self.__class__.__name__)
        logger.debug("Method authenticate start.")
        logger.debug("Method authenticate end.")

    def validate_domain(self):
        logger = logging.getLogger('%s.validate_domain' % self.__class__.__name__)
        logger.debug("Method validate_domain start.")
        logger.debug("Method validate_domain end.")

    def get_records(self):
        logger = logging.getLogger('%s.get_records' % self.__class__.__name__)
        logger.debug("Method get_records start.")
        logger.debug("Method get_records end.")

    def update_record(self):
        logger = logging.getLogger('%s.update_record' % self.__class__.__name__)
        logger.debug("Method update_record start.")
        logger.debug("Method update_record end.")

    def logout(self):
        logger = logging.getLogger('%s.logout' % self.__class__.__name__)
        logger.debug("Method logout start.")
        logger.debug("Method logout end.")
