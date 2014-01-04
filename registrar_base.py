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
        self.recorded_ips = list()  # [RegistrarBase.Record(), ...]
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

    class Payload(object):
        """Bare-bones class to hold the raw data from the API as well as parsed JSON."""
        def __init__(self, original_url, actual_url, post_data, response):
            self.original_url = original_url
            self.actual_url = actual_url
            self.post_data = post_data
            self.response = response
            self.json = dict()
            
        def parse(self):
            self.json = json.loads(self.response)

        def __eq__(self, other):
            return (type(other) is type(self) and self.__dict__ == other.__dict__) or NotImplemented

        def __ne__(self, other):
            return (self.__eq__(other) == NotImplemented) or NotImplemented

    class Record(object):
        """Bare-bones class to hold a record and some attributes."""
        def __init__(self, record_id, record_type, name, content):
            self.id = record_id
            self.type = record_type
            self.name = name
            self.content = content

        def __eq__(self, other):
            return (type(other) is type(self) and self.__dict__ == other.__dict__) or NotImplemented

        def __ne__(self, other):
            return (self.__eq__(other) == NotImplemented) or NotImplemented

    class RegistrarException(Exception):
        """Exception to be raised inside RegistrarBase and its derivatives when a handled error occurs."""
        pass

    def _request_json(self, url, post_data=None):
        """Handles HTTP connections and returns a Payload instance."""
        logger = logging.getLogger('%s._request_json' % __name__)
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
        payload = self.Payload(url, response.geturl(), post_data, response.read())
        try:
            payload.parse()
        except ValueError:
            logger.debug("Response: %s" % payload.response)
            raise self.RegistrarException("Invalid JSON.")
        return payload

    def get_current_ip(self):
        logger = logging.getLogger('%s.get_current_ip' % __name__)
        logger.debug("Method get_current_ip start.")
        data = self._request_json(self._url_get_current_ip)
        logger.debug("Response: %s" % data.response)
        logger.debug("JSON: %s" % data.json)
        if 'client_ip' not in data.json:
            raise self.RegistrarException("'client_ip' not in JSON.")
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", data.json['client_ip']):
            raise self.RegistrarException("'client_ip' is not an IP address.")
        self.current_ip = data.json['client_ip']
        logger.debug("Method get_current_ip end.")

    def authenticate(self):
        logger = logging.getLogger('%s.authenticate' % __name__)
        logger.debug("Method authenticate start.")
        post_data = json.dumps(dict(username=self.config['user'], api_token=self.config['passwd']))
        data = self._request_json(self._url_authenticate, post_data)
        if 'session_token' not in data.json:
            logger.debug("Response: %s" % data.response)
            logger.debug("JSON: %s" % data.json)
            raise self.RegistrarException("'session_token' not in JSON.")
        if not re.match(r"^([A-Fa-f0-9]){10,46}$", data.json['session_token']):
            logger.debug("Response: %s" % data.response)
            logger.debug("JSON: %s" % data.json)
            raise self.RegistrarException("'session_token' is invalid.")
        self._session_token = data.json['session_token']
        logger.debug("Method authenticate end.")

    def validate_domain(self):
        logger = logging.getLogger('%s.validate_domain' % __name__)
        logger.debug("Method validate_domain start.")
        data = self._request_json(self._url_get_main_domain)
        logger.debug("Response: %s" % data.response)
        logger.debug("JSON: %s" % data.json)
        candidates = [d for d in data.json.get('domains', {}).keys() if self.config['domain'].endswith(d)]
        if len(candidates) < 1:
            raise self.RegistrarException("Domain not registered to this registrar's account.")
        if len(candidates) > 1:
            logger.error("Cannot figure out main domain: %s" % candidates)
            raise ValueError
        self._main_domain = candidates[0]
        logger.debug("Method validate_domain end.")

    def get_records(self):
        logger = logging.getLogger('%s.get_records' % __name__)
        logger.debug("Method get_records start.")
        data = self._request_json(self._url_get_records_prefix + self._main_domain)
        logger.debug("Response: %s" % data.response)
        logger.debug("JSON: %s" % data.json)
        for r in data.json.get('records', {}):
            if r['name'] != self.config['domain'] or r['type'] not in ('A', 'CNAME'):
                continue
            self.recorded_ips.append(self.Record(r['record_id'], r['type'], r['name'], r['content']))
        logger.debug("Method get_records end.")

    def create_record(self):
        logger = logging.getLogger('%s.create_record' % __name__)
        logger.debug("Method create_record start.")
        hostname = re.sub(self._main_domain + r"$", '', self.config['domain']).strip('.') or '.'
        post_data = json.dumps(dict(hostname=hostname, type='A', content=self.current_ip, ttl=300, priority=10))
        logger.debug("Sending POST data: %s" % post_data)
        data = self._request_json(self._url_create_record_prefix + self._main_domain, post_data)
        logger.debug("Response: %s" % data.response)
        logger.debug("JSON: %s" % data.json)
        logger.debug("Method create_record end.")

    def delete_record(self, record_id):
        logger = logging.getLogger('%s.delete_record' % __name__)
        logger.debug("Method delete_record start.")
        post_data = json.dumps(dict(record_id=record_id))
        logger.debug("Sending POST data: %s" % post_data)
        data = self._request_json(self._url_delete_record_prefix + self._main_domain, post_data)
        logger.debug("Response: %s" % data.response)
        logger.debug("JSON: %s" % data.json)
        logger.debug("Method delete_record end.")

    def logout(self):
        logger = logging.getLogger('%s.logout' % __name__)
        logger.debug("Method logout start.")
        self._request_json(self._url_logout)
        self._session_token = None
        logger.debug("Method logout end.")
