#!/usr/bin/env python2.6
"""Name.com class for UnofficialDDNSnix.
https://github.com/Robpol86/UnofficialDDNSnix
"""


from registrar_base import RegistrarBase
import logging


class RegistrarName(RegistrarBase):

    _url_base = "https://api.name.com/api"
    _url_get_current_ip = _url_base + "/hello"
    _url_authenticate = _url_base + "/login"
    _url_get_main_domain = _url_base + "/domain/list"
    _url_get_records_prefix = _url_base + "/dns/list/"
    _url_delete_record_prefix = _url_base + "/dns/delete/"
    _url_create_record_prefix = _url_base + "/dns/create/"
    _url_logout = _url_base + "/logout"

    def _request_json(self, url, post_data=None):
        """All top-level API JSON responses are expected to be dictionaries, not lists."""
        logger = logging.getLogger('%s._request_json' % __name__)
        data = super(RegistrarName, self)._request_json(url, post_data)
        if not isinstance(data.json, dict):
            logger.debug("Response: %s" % data.response)
            logger.debug("JSON: %s" % data.json)
            raise self.RegistrarException("Unexpected JSON format. Expected top-level to be a dictionary.")
        if data.json.get('result', {}).get('code') == 221:
            logger.debug("Response: %s" % data.response)
            logger.debug("JSON: %s" % data.json)
            raise self.RegistrarException("Authorization Error or invalid username and/or password.")
        if [data.json.get('result', {}).get(k) for k in ('message', 'code')] != ['Command Successful', 100]:
            logger.debug("Response: %s" % data.response)
            logger.debug("JSON: %s" % data.json)
            raise self.RegistrarException("API returned an error.")
        return data